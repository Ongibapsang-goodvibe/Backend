# restaurants/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .serializers import SearchInputSerializer, MenuCardSerializer
from .services_search import simple_three_way_search

#프론트에서 Json으로 호출하는 api 
#서비스 호출 -> 시리얼라이저로 응답

class SearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = SearchInputSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        kw = s.validated_data["text"]
        limit = s.validated_data.get("limit", 10)

        stage, qs = simple_three_way_search(keyword=kw, limit=limit)
        data = MenuCardSerializer(qs, many=True).data
        return Response({"stage": stage, "cards": data}, status=status.HTTP_200_OK)
    

