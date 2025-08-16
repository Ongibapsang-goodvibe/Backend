# restaurant/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from voice.models import Transcription
from .serializers import SearchInputSerializer, MenuCardSerializer
from .services_search import simple_three_way_search

#프론트에서 Json으로 호출하는 api 
class SearchByTranscriptionView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = SearchInputSerializer(data=request.data)
        s.is_valid(raise_exception=True)
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