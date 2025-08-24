import os
import uuid
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
import openai
from .models import ChatMessage

openai.api_key = os.getenv("OPENAI_API_KEY")

ALLOWED_AUDIO_EXTENSIONS = ['mp3', 'wav', 'm4a', 'ogg', 'webm']

class ProcessAudioAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # 1. 음성 파일 저장
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return Response({"error": "오디오 파일이 필요합니다."}, status=400)

        ext = audio_file.name.split('.')[-1].lower()
        if ext not in ALLOWED_AUDIO_EXTENSIONS:
            return Response({"error": "허용되지 않는 오디오 파일 형식입니다."}, status=400)

        # 파일 저장 (UUID로 중복 방지)
        file_name = f"{uuid.uuid4()}.{ext}"
        file_path = default_storage.save(file_name, ContentFile(audio_file.read()))
        full_path = os.path.join(default_storage.location, file_path)

        # 2. Whisper로 음성 -> 텍스트 변환
        try:
            with open(full_path, "rb") as f:
                transcript = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=f
                )
            user_text = transcript.text
        except Exception as e:
            return Response({"error": f"Whisper 처리 실패: {e}"}, status=500)

        # DB에 사용자 메시지 저장
        ChatMessage.objects.create(role='user', content=user_text)

        # 이전 대화 가져오기(최근 10개) -> 대화 이어서 전송
        previous_messages = ChatMessage.objects.all().order_by('-created_at')[:10]
        messages_for_gpt = [
            {"role": "system", "content": "최대한 귀엽고 높은 톤과 함께 존댓말로 천천히 말해주세요. 답변 시간은 15초 이내로 해주세요. 대화를 계속 이어가주세요."}
        ]
        for msg in reversed(previous_messages):
            messages_for_gpt.append({
                "role": "assistant" if msg.role == "assistant" else "user",
                "content": msg.content
            })

        # 3. GPT 응답 생성
        try:
            chat_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages_for_gpt
            )
            answer_text = chat_response.choices[0].message.content
        except Exception as e:
            return Response({"error": f"GPT 처리 실패: {e}"}, status=500)

        # DB에 AI 메시지 저장
        ChatMessage.objects.create(role='assistant', content=answer_text)

        # 4. TTS로 mp3 생성
        tts_file_name = f"{uuid.uuid4()}.mp3"
        speech_file_path = os.path.join(default_storage.location, tts_file_name)
        try:
            with open(speech_file_path, "wb") as f:
                tts = openai.audio.speech.create(
                    model="gpt-4o-mini-tts",
                    voice="sage",
                    input=answer_text,
                )
                f.write(tts.read())
        except Exception as e:
            return Response({"error": f"TTS 처리 실패: {e}"}, status=500)
        # 5. mp3 URL 반환
        return Response({
            "answer": answer_text,
            "audio_url": f"/media/{tts_file_name}"
        })

#대화 강제 종료
class EndChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ChatMessage.objects.all().delete()
        return Response({"status": "chat_ended"})
