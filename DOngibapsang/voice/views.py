# voice/views.py
import os, requests
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from .models import Transcription

class TranscribeView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        audio = request.FILES.get("audio")
        if not audio:
            return Response({"error":"audio file required"}, status=400)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return Response({"error":"OPENAI_API_KEY missing"}, status=500)

        intent = request.data.get("intent", Transcription.Intent.UNKNOWN)
        language = request.data.get("language", "ko")

        audio_bytes = audio.read()  # 한 번만 읽고 Whisper/DB 둘 다 사용
        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {api_key}"}
        files = {"file": (audio.name, audio_bytes, audio.content_type or "application/octet-stream")}
        data = {"model": "whisper-1", "language": language}

        try:
            r = requests.post(url, headers=headers, files=files, data=data, timeout=90)
            r.raise_for_status()
            text = (r.json().get("text") or "").strip()
        except requests.RequestException as e:
            return Response({"error": f"whisper: {e}"}, status=502)

        if not text:
            return Response({"error":"speech not recognized"}, status=400)

        # 전사 결과를 DB에 저장 
        tr = Transcription.objects.create(
            user=request.user if request.user.is_authenticated else None, #로그인 사용자가 있으면 연결 
            text=text, #전사 텍스트 
            intent=intent, meta={"scenario": intent}
        )
        tr.audio_file.save(audio.name, ContentFile(audio_bytes), save=True)

        # 전사한 원문 텍스트만 전달 
        return Response({"id": tr.id, "text": text, "intent": intent}, status=201)