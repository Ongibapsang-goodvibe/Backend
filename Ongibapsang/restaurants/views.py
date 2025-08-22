from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated

from .models import * 
from .serializers import SearchInputSerializer, MenuCardSerializer
from .services_search import simple_three_way_search
from .recommendation import main_recommend

# 메뉴 검색 결과 뷰 
class SearchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = SearchInputSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        kw = s.validated_data["text"]
        limit = s.validated_data.get("limit", 10)

        stage, qs = simple_three_way_search(keyword=kw, limit=limit)
        data = MenuCardSerializer(qs, many=True).data
        return Response({"stage": stage, "cards": data}, status=status.HTTP_200_OK)
    
# 메뉴 카테고리별 분류 
class CategoryView(ListAPIView):
        permission_classes = [IsAuthenticated]
        serializer_class = MenuCardSerializer
        
        def get_queryset(self):
            codes = self.request.query_params.getlist("category")

            if not codes:
                return Menu.objects.none()
            return Menu.objects.filter(category__in=codes).order_by("id")

        # SearchView와 동일한 응답 형태로 통일
        def list(self, request, *args, **kwargs):
            qs = self.get_queryset()
            data = self.get_serializer(qs, many=True).data
            return Response({"cards": data}, status=status.HTTP_200_OK)


class RecommendMenuView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rec = main_recommend(request.user, limit=10)
        return Response(rec)