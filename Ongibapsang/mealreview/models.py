from django.db import models
from django.conf import settings
from orders.models import Order


#피드백 입력 경로
class Source(models.TextChoices):
    BUTTON = "BUTTON", "버튼"
    VOICE = "VOICE", "음성"

# 상위 감정(양쪽 코드 공통 분모)
class Sentiment(models.TextChoices):
    GOOD = "GOOD", "잘 먹었어요"
    BAD  = "BAD",  "별로였어요"


# 세부 선택 옵션(상대방 ReviewOption 모델 의도 + 너의 DetailOption 역할)
class ReviewOption(models.Model):
    # ex) liked_dish, too_salty
    key = models.SlugField(unique=True)
    label = models.CharField(max_length=30)                 # 버튼에 보이는 텍스트
    kind = models.CharField(max_length=4, choices=Sentiment.choices)  # GOOD/BAD
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["kind", "sort_order", "id"]

    def __str__(self):
        return f"[{self.kind}] {self.label}"


# (과도기 호환) 예전 코드가 DetailOption을 참조해도 깨지지 않게 Proxy 제공
class DetailOption(ReviewOption):
    class Meta:
        proxy = True
        verbose_name = "Detail Option"
        verbose_name_plural = "Detail Options"

    # 예전 코드 호환용: initial_label → kind
    @property
    def initial_label(self) -> str:
        return self.kind


# DB 저장용 로그 (양쪽 의도 통합)
class MealLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="meal_logs",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="meal_logs",
    )
    initial_label = models.CharField(           # 상위 감정
        max_length=30, choices=Sentiment.choices
    )
    source = models.CharField(
        max_length=6, choices=Source.choices, default=Source.BUTTON
    )
    option = models.ForeignKey(                 # 세부 옵션
        ReviewOption, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="meal_logs"
    )
    option_label = models.CharField(max_length=30, blank=True)
    text = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.option and not self.option_label:
            self.option_label = self.option.label
        super().save(*args, **kwargs)

    def __str__(self):
        return self.option_label or (self.text[:10] + "…")