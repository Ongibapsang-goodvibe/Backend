import os
import requests
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from .models import Transcription


# Create your views here.
class TranscribeView(APIView):
    # 업로드가 multipart/form-data로 올 때 파싱해 주는 DRF 파서
    parser_classes = [MultiPartParser]

    def post(self, request):
        # 1) 파일 존재 확인
        audio = request.FILES.get("audio")
        if not audio:
            return JsonResponse({"error":"audio file required"}, status=400)

        # 2) 환경변수에서 API 키 읽기 (.env + load_dotenv()가 필요)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return JsonResponse({"error":"OPENAI_API_KEY missing"}, status=500)
        
        # 3) Whisper API 엔드포인트/헤더
        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {api_key}"}
        files = {
            "file": (audio.name, audio.read(), audio.content_type),
            "model": (None, "whisper-1"),
            "language": (None, "ko"),
        }

        # Whisper 호출 
        try:
            r = requests.post(url, headers=headers, files=files, timeout=90)
            r.raise_for_status()
            #응답에서 텍스트만 꺼냄 
            text = (r.json().get("text") or "").strip()
        except requests.RequestException as e:
            return JsonResponse({"error": f"whisper: {e}"}, status=502)

        # (선택) 간단 분류/키워드 추출
        intent, meta = "UNKNOWN", {}
        # intent, meta = classify(text)  # 필요시 이후 추가

        # DB 저장
        tr = Transcription.objects.create(
            user=request.user if request.user.is_authenticated else None,
            audio_file=audio,  # FileField 저장 위해서는 InMemoryUploadedFile 그대로 써도 OK
            text=text, intent=intent, meta=meta
        )
        return JsonResponse({"id": tr.id, "text": text, "intent": intent, "meta": meta}, status=201)