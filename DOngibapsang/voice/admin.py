from django.contrib import admin
from .models import Transcription

# voice/admin.py
@admin.register(Transcription)
class TranscriptionAdmin(admin.ModelAdmin):
    list_display = ("id","intent","created_at")
    readonly_fields = ("text",)  # 편집 방지 + 그대로 보여주기
    search_fields = ("text",)