from django.db import models
from django.conf import settings

# Create your models here.

#피드백 입력 경로
class Source(models.TextChoices):
    BUTTON = "BUTTON", "버튼"
    VOICE = "VOICE", "음성"

# 첫 화면 버튼 
class ReviewOption(models.Model):
    label = models.CharField(max_length=20) #초기 버튼 라벨(잘 먹었어요 or 별로였어요)
    sort_order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.label

#세부 선택 옵션 
class DetailOption(models.Model):
    label = models.CharField(max_length=20)
    initial_label = models.CharField(max_length=30, db_index=True)  # "잘 먹었어요" | "별로였어요"
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["initial_label", "sort_order", "id"]

    def __str__(self):
        return f"[{self.initial_label}] {self.label}"

#DB 저장용 로그 
class MealLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.SET_NULL, related_name="meal_logs")
    # 주문/식당/메뉴 FK 필요하면 추가(주문 기록 가져오는 방법은?)
    initial_label = models.CharField(max_length=30, blank=True)
    source = models.CharField(max_length=6, choices=Source.choices, default=Source.BUTTON)
    option = models.ForeignKey(DetailOption, on_delete=models.SET_NULL, null=True, blank=True)
    option_label = models.CharField(max_length=30, blank=True)
    text = models.CharField(max_length=255, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
   
    def save(self, *args, **kwargs):
        if self.option and not self.option_label:
            self.option_label = self.option.label
        super().save(*args, **kwargs)

    def __str__(self):
        return self.option_label or (self.text[:10] + "…")