<<<<<<< HEAD
# restaurants/views.py
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import * 
from .serializers import SearchInputSerializer, MenuCardSerializer
from .services_search import simple_three_way_search

# 메뉴 검색 결과 뷰 
class SearchView(APIView):
=======
# restaurant/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated
from voice.models import Transcription
from .serializers import SearchInputSerializer, MenuCardSerializer
from .services_search import simple_three_way_search
from .recommendation import main_recommend

class RecommendMenuView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rec = main_recommend(request.user, limit=10)
        return Response(rec)

#프론트에서 Json으로 호출하는 api 
class SearchByTranscriptionView(APIView):
>>>>>>> origin/backup_0821
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = SearchInputSerializer(data=request.data)
        s.is_valid(raise_exception=True)
<<<<<<< HEAD
        kw = s.validated_data["text"]
        limit = s.validated_data.get("limit", 10)

        stage, qs = simple_three_way_search(keyword=kw, limit=limit)
        data = MenuCardSerializer(qs, many=True).data
        return Response({"stage": stage, "cards": data}, status=status.HTTP_200_OK)
    
# 메뉴 카테고리별 분류 
class CategoryView(ListAPIView):
        permission_classes = [permissions.AllowAny]
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
=======
        limit = s.validated_data.get("limit", 10)

        tr = None
        keyword = s.validated_data.get("text")
        if not keyword:
            tr = Transcription.objects.filter(pk=s.validated_data["transcription_id"]).first()
            if not tr:
                return Response({"detail": "transcription not found"}, status=404)
            keyword = (tr.text or "").strip()

        result = simple_three_way_search(keyword=keyword, transcription=tr, limit=limit)
        return Response({
            "transcription_id": tr.id if tr else None,
            "stage": result["stage"],
            "log": result["log"],  # ← 프론트에서 로그도 함께 사용 가능
            "cards": MenuCardSerializer(result["cards"], many=True).data,
        }, status=200)
>>>>>>> origin/backup_0821
