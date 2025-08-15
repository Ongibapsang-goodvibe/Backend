import asyncio
import websockets
import json
import base64
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Ongibapsang.settings")
django.setup()

async def test():
    uri = "ws://127.0.0.1:8000/ws/chat/"  # Django runserver 주소
    async with websockets.connect(uri, max_size=10 * 1024 * 1024) as websocket:  # 10MB 제한
        with open("속이 안 좋아.mp3", "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode('utf-8')

        message = {
            "user_name": "TestUser",
            "audio": audio_base64
        }

        await websocket.send(json.dumps(message))
        print("메시지 전송 완료")

        try:
            response = await websocket.recv()
            print("Received:", response)

            data = json.loads(response)
            print("Whisper 텍스트:", data.get("user_text"))
            print("GPT 응답:", data.get("ai_text"))

            # AI 음성 파일 저장
            with open("ai_response.mp3", "wb") as f:
                f.write(base64.b64decode(data["ai_audio_base64"]))
            print("AI 음성 파일(ai_response.mp3) 저장 완료")

        except websockets.exceptions.ConnectionClosedError as e:
            print("Connection closed unexpectedly:", e)

asyncio.run(test())