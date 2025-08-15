import openai
import os

# 환경변수로 OPENAI_API_KEY 설정되어 있다면 이렇게 불러옴
openai.api_key = "OPENAI_API_KEY"

with open("C:/Users/samsung/Downloads/voice_test.mp3", "rb") as audio_file:
    transcript = openai.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )

print(transcript.text)
