# voice/management/commands/transcribe.py
import os, mimetypes, json
from glob import iglob
from pathlib import Path
import requests

from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model

from voice.models import Transcription  # Intent는 내부 Enum

AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".webm", ".ogg", ".flac", ".aac"}

def _iter_input_files(inputs):
    files = []
    for inp in inputs:
        p = Path(inp)
        if any(ch in inp for ch in "*?[]"):
            for x in iglob(inp, recursive=True):
                px = Path(x)
                if px.is_file() and px.suffix.lower() in AUDIO_EXTS:
                    files.append(px)
        elif p.is_dir():
            for ext in AUDIO_EXTS:
                files.extend(p.rglob(f"*{ext}"))
        elif p.is_file() and p.suffix.lower() in AUDIO_EXTS:
            files.append(p)
    return sorted(set(Path(f) for f in files))

def _guess_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or ("audio/mpeg" if path.suffix.lower() == ".mp3" else "application/octet-stream")

def transcribe_with_whisper(file_path: Path, api_key: str, model="whisper-1", language=None, timeout=120) -> str:
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}
    mime = _guess_mime(file_path)
    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f, mime)}
        data = {"model": model}
        if language:
            data["language"] = language
        r = requests.post(url, headers=headers, files=files, data=data, timeout=timeout)
        r.raise_for_status()
        return (r.json().get("text") or "").strip()

class Command(BaseCommand):
    help = "Transcribe audio(s) with Whisper, save Transcription, and optionally run a domain action (e.g., ORDER search)."

    def add_arguments(self, parser):
        parser.add_argument("inputs", nargs="+", help="files/dirs/globs (e.g. data/*.mp3)")
        parser.add_argument("--user-id", type=int, default=None)
        # ✅ intent 옵션 제거 (전사 단계는 intent-중립)
        parser.add_argument("--language", type=str, default="ko")
        parser.add_argument("--model", type=str, default="whisper-1")
        parser.add_argument("--no-save-file", action="store_true", help="Don't store original audio in DB")
        # (선택) 예전 도움말 혼동 방지: intent 조건 문구 제거
        # parser.add_argument("--search", action="store_true", help="(deprecated)")
        parser.add_argument("--limit", type=int, default=10, help="Cards to print when --action")
        # ✅ intent-중립을 지키면서 필요한 도메인만 실행
        parser.add_argument(
            "--action",
            choices=["none", "order_search"],
            default="none",
            help="After saving, run a domain action (default: none)"
        )
        parser.add_argument("--json", action="store_true", help="With --action, print domain result as JSON")

    def handle(self, *args, **opts):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise CommandError("OPENAI_API_KEY is missing")

        user = None
        if opts["user_id"] is not None:
            User = get_user_model()
            try:
                user = User.objects.get(pk=opts["user_id"])
            except User.DoesNotExist:
                raise CommandError(f"User not found: id={opts['user_id']}")

        files = _iter_input_files(opts["inputs"])
        if not files:
            raise CommandError("No audio files found.")

        self.stdout.write(self.style.NOTICE(f"Found {len(files)} audio file(s)."))

        # 필요할 때만 도메인 의존성 로딩
        simple_three_way_search = None
        MenuCardSerializer = None
        if opts["action"] == "order_search":
            try:
                from restaurants.services_search import simple_three_way_search as _search
                from restaurants.serializers import MenuCardSerializer as _card_ser
                simple_three_way_search = _search
                MenuCardSerializer = _card_ser
            except Exception as e:
                raise CommandError(f"Import restaurants.* failed: {e}")

        successes, failures = 0, 0
        for path in files:
            try:
                self.stdout.write(f"[Transcribe] {path.name}")
                text = transcribe_with_whisper(
                    path, api_key, model=opts["model"], language=opts["language"]
                )
                if not text:
                    self.stderr.write(self.style.WARNING("  -> empty transcript (skip)"))
                    failures += 1
                    continue

                # ✅ 전사만 저장: intent는 UNKNOWN(또는 모델 기본값)
                tr = Transcription.objects.create(
                    user=user,
                    text=text,
                    intent=Transcription.Intent.UNKNOWN,   # ← 고정/수신 금지
                    meta={"via": "mgmt:transcribe"},       # ← scenario는 앱 단계에서 세팅
                )

                if not opts.get("no_save_file", False):
                    with open(path, "rb") as f:
                        tr.audio_file.save(path.name, ContentFile(f.read()), save=True)

                self.stdout.write(self.style.SUCCESS(f"  -> T#{tr.id} text='{text}'"))

                # 공용 페이로드
                base_payload = {"transcription_id": tr.id, "intent": tr.intent, "text": text}

                # ✅ 도메인 액션: 의도 검사 없이, 명시된 action일 때만 실행
                if opts["action"] == "order_search" and simple_three_way_search:
                    result = simple_three_way_search(keyword=text, transcription=tr, limit=opts["limit"])
                    if opts.get("json") and MenuCardSerializer:
                        payload = {
                            **base_payload,
                            "result": {
                                "type": "restaurant.cards",
                                "stage": result["stage"],
                                "log": result.get("log"),
                                "cards": MenuCardSerializer(result["cards"], many=True).data,
                            }
                        }
                        print(json.dumps(payload, ensure_ascii=False, indent=2))
                    else:
                        self.stdout.write(self.style.HTTP_INFO(f"    stage: {result['stage']}"))
                        for card in result["cards"]:
                            self.stdout.write(
                                f"    - {card['menu_name']} / {card['restaurant_name']} (₩{card['price']})"
                            )

                successes += 1

            except requests.RequestException as e:
                self.stderr.write(self.style.ERROR(f"whisper failed for {path.name}: {e}"))
                failures += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"failed on {path.name}: {e}"))
                failures += 1

        self.stdout.write(self.style.SUCCESS(f"Done. success={successes}, failed={failures}"))
