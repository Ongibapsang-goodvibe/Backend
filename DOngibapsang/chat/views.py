import openai
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import ChatMessage

openai.api_key = os.getenv("OPENAI_API_KEY")

def index(request):
    return render(request, 'index.html')

@csrf_exempt
def process_audio(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        # 1. 음성 파일 저장
        audio_file = request.FILES['audio']
        file_path = default_storage.save('temp_audio.wav', ContentFile(audio_file.read()))
        full_path = os.path.join(default_storage.location, file_path)

        # 2. Whisper로 음성 → 텍스트 변환
        with open(full_path, "rb") as f:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        user_text = transcript.text

        # DB에 사용자 메시지 저장
        ChatMessage.objects.create(role='user', content=user_text)

        # 이전 대화 가져오기 -> 대화 이어서 전송
        previous_messages = ChatMessage.objects.all().order_by('created_at')
        messages_for_gpt = [{"role": "system", "content": "너는 친절한 챗봇이야."}]
        for msg in previous_messages:
            messages_for_gpt.append({
                "role": "assistant" if msg.role == "ai" else "user", 
                "content": msg.content
            })

        # 3. GPT 응답 생성
        chat_response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_for_gpt
        )
        answer_text = chat_response.choices[0].message.content

        # DB에 AI 메시지 저장
        ChatMessage.objects.create(role='assistant', content=answer_text)

        # 4. TTS로 mp3 생성
        speech_file_path = os.path.join(default_storage.location, "response.mp3")
        with open(speech_file_path, "wb") as f:
            tts = openai.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice="alloy",
                input=answer_text
            )
            f.write(tts.read())

        # 5. mp3 URL 반환
        return JsonResponse({
            "answer": answer_text,
            "audio_url": f"/media/response.mp3"
        })

    return JsonResponse({"error": "No audio uploaded"}, status=400)

#대화 강제 종료
@csrf_exempt
def end_chat(request):
    if request.method == 'POST':
        ChatMessage.objects.all().delete()
        return JsonResponse({"status": "chat_ended"})
    return JsonResponse({"error": "Invalid request"}, status=400)