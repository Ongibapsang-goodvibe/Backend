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
    
    
# healthcare/models.py

class DiseaseRules(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name="disease_rules")
    nutrient = models.ForeignKey("restaurants.Nutrient", on_delete=models.CASCADE, related_name="nutrient_rules")

    # 절대량(1회 제공량 기준, mg)
    min_once = models.FloatField(null=True, blank=True, help_text="1회 제공 최소 섭취량 (mg 단위)")
    max_once = models.FloatField(null=True, blank=True, help_text="1회 제공 최대 섭취량 (mg 단위)")

    # 비율(열량 대비 %)
    percent_min = models.FloatField(null=True, blank=True, help_text="열량 대비 최소 비율 (%)")
    percent_max = models.FloatField(null=True, blank=True, help_text="열량 대비 최대 비율 (%)")

    # 1000kcal 기준
    use_per_1000kcal = models.BooleanField(default=False)
    per_1000kcal_min = models.FloatField(null=True, blank=True, help_text="1000kcal 당 최소 (mg 단위)")
    per_1000kcal_max = models.FloatField(null=True, blank=True, help_text="1000kcal 당 최대 (mg 단위)")

    note = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        unique_together = ("disease", "nutrient")

    # ✅ 계산 프로퍼티: 현재 설정을 기반으로 rule_type 판별
    @property
    def rule_type(self) -> str:
        if self.use_per_1000kcal or self.per_1000kcal_min is not None or self.per_1000kcal_max is not None:
            return "PER_1000KCAL"
        if self.percent_min is not None or self.percent_max is not None:
            return "PERCENT"
        if self.min_once is not None or self.max_once is not None:
            return "ABS_ONCE"
        return "UNSET"

    def __str__(self):
        return f"{self.disease.name} - {self.nutrient.name} ({self.rule_type})"

    
class NutritionReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="users_with_diseases")
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name="users_disease")
    date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "disease")
    
    def __str__(self):
        return f"{self.user} - {self.disease.name}"
