from django.db import models
from django.conf import settings
from orders.models import Order

# Create your models here.
# 질환 모델 
class Disease(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name
    

# 첫 화면 버튼(몸 상태 확인)
class HealthcareOption(models.TextChoices):
    GOOD = "GOOD", "아무 문제 없어요"
    BAD = "BAD", "어딘가 불편해요"

    
# 기분 선택 옵션
class MoodOption(models.TextChoices):
    GREAT = "GREAT", "최고예요!"
    FINE = "FINE", "괜찮아요"
    SOSO = "SOSO", "그냥 그래요"
    BAD = "BAD", "안 좋아요"
    TERRIBLE = "TERRIBLE", "나빠요"

# DB 저장용 로그
class HealthcareLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                             on_delete=models.SET_NULL, related_name="healthcare_logs")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True,blank=True)
    initial_label=models.CharField(max_length=20, choices=HealthcareOption.choices) #아무 문제 없어요 or 어딘가 불편해요 
    text= models.CharField(max_length=255, blank=True) # 어딘가 불편해요 선택 시 음성 텍스트 
    mood_label = models.CharField(max_length=20, choices=MoodOption.choices, null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
