from django.db import models
from django.conf import settings

# Create your models here.
# Transcription 모델 -> whisper에서 전사한 원문 텍스트 
class Transcription(models.Model):
    class Intent(models.TextChoices):
        UNKNOWN = "UNKNOWN"
        ORDER = "ORDER"
        DELIVERY_REVIEW = "DELIVERY_REVIEW"
        MEAL_REVIEW = "MEAL_REVIEW"
        HEALTHCARE = "HEALTHCARE"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    audio_file = models.FileField(upload_to="voice/", blank=True)
    text = models.TextField(blank=True) # 가공 없는 텍스트 저장 
    intent = models.CharField(max_length=20, choices=Intent.choices, default=Intent.UNKNOWN)
    meta = models.JSONField(default=dict, blank=True)   # 주문, 배달리뷰, 음식리뷰, 안부 
    created_at = models.DateTimeField(auto_now_add=True)
