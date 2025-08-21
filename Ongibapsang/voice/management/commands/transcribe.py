import os
import mimetypes
from glob import iglob
from pathlib import Path

import requests
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model

from voice.models import Transcription  # Intent를 모델 내부 Enum으로 정의했다면 이대로 OK
# 만약 Intent가 별도 클래스로 분리되어 있다면: from voice.models import Transcription, Intent

AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".webm", ".ogg", ".flac", ".aac"}

def _iter_input_files(inputs):
    """파일/디렉토리/글롭 패턴을 받아 실제 오디오 파일 경로들로 펼친다."""
    files = []
    for inp in inputs:
        p = Path(inp)
        # 글롭 패턴
        if any(ch in inp for ch in "*?[]"):
            for x in iglob(inp, recursive=True):
                px = Path(x)
                if px.is_file() and px.suffix.lower() in AUDIO_EXTS:
                    files.append(px)
        # 디렉토리
        elif p.is_dir():
            for ext in AUDIO_EXTS:
                files.extend(p.rglob(f"*{ext}"))
        # 단일 파일
        elif p.is_file() and p.suffix.lower() in AUDIO_EXTS:
            files.append(p)
        else:
            # 무시(확장자 미지원/존재X)
            continue
    # 중복 제거 + 정렬
    return sorted(set(Path(f) for f in files))

def _guess_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    # 기본값: audio/mpeg (mp3), 없으면 application/octet-stream
    return mime or ("audio/mpeg" if path.suffix.lower() == ".mp3" else "application/octet-stream")

def transcribe_with_whisper(file_path: Path, api_key: str, model="whisper-1", language=None, timeout=90) -> str:
    """OpenAI Whisper API 호출: 파일 1개 → 텍스트"""
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}
    mime = _guess_mime(file_path)

    with open(file_path, "rb") as f:
        files = {
            "file": (file_path.name, f, mime),
        }
        data = {"model": model}
        if language:
            data["language"] = language  # 예: "ko"

        r = requests.post(url, headers=headers, files=files, data=data, timeout=timeout)
        r.raise_for_status()
        return (r.json().get("text") or "").strip()

class Command(BaseCommand):
    help = "Transcribe one or more local audio files with Whisper and save them to DB."

    def add_arguments(self, parser):
        # 여러 입력 경로를 허용: 파일/디렉토리/글롭
        parser.add_argument("inputs", nargs="+", help="files/dirs/globs (e.g. data/*.mp3)")
        parser.add_argument("--user-id", type=int, default=None, help="Owner user id (optional)")
        parser.add_argument("--scenario", type=str, default=None,
                            help="Scenario hint for classifier (e.g. SEARCH|ORDER|DELIVERY_REVIEW|MEAL_REVIEW|HEALTHCARE)")
        parser.add_argument("--model", type=str, default="whisper-1", help="Whisper model name")
        parser.add_argument("--language", type=str, default=None, help="Language hint (e.g. ko)")
        parser.add_argument("--no-save-file", action="store_true", help="Do not store original audio in DB")

    def handle(self, *args, **opts):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise CommandError("OPENAI_API_KEY is missing. Put it in your .env and load it before running Django.")

        # 사용자 선택적 지정
        user = None
        if opts["user_id"] is not None:
            User = get_user_model()
            try:
                user = User.objects.get(pk=opts["user_id"])
            except User.DoesNotExist:
                raise CommandError(f"User not found: id={opts['user_id']}")

        files = _iter_input_files(opts["inputs"])
        if not files:
            raise CommandError("No audio files found for given inputs.")

        self.stdout.write(self.style.NOTICE(f"Found {len(files)} audio file(s)."))

        successes, failures = 0, 0
        for path in files:
            try:
                self.stdout.write(f"Transcribing: {path}")
                text = transcribe_with_whisper(
                    path, api_key, model=opts["model"], language=opts["language"]
                )

                # meta에 scenario 힌트 포함(분류기 보정용)
                meta = {}
                if opts.get("scenario"):
                    meta["scenario"] = opts["scenario"]

                # Transcription 저장 (post_save 시그널이 분류/라우팅 실행)
                tr = Transcription.objects.create(
                    user=user,
                    text=text,
                    # 의도는 UNKNOWN으로 두고 시그널에서 결정
                    intent=getattr(Transcription, "Intent", None).UNKNOWN if hasattr(Transcription, "Intent") else "UNKNOWN",
                    meta=meta,
                )

                if not opts["no_save_file"]:
                    with open(path, "rb") as f:
                        tr.audio_file.save(path.name, ContentFile(f.read()), save=True)

                self.stdout.write(self.style.SUCCESS(f"[#{tr.id}] {path.name} ✓"))
                successes += 1

            except requests.RequestException as e:
                self.stderr.write(self.style.ERROR(f"Whisper request failed for {path}: {e}"))
                failures += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed on {path}: {e}"))
                failures += 1

        self.stdout.write(self.style.SUCCESS(f"Done. success={successes}, failed={failures}"))