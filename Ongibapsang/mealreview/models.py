from django.db import models
from django.conf import settings
from orders.models import Order

# Create your models here.

#피드백 입력 경로
class Source(models.TextChoices):
    BUTTON = "BUTTON", "버튼"
    VOICE = "VOICE", "음성"

# 첫 화면 버튼 
class ReviewOption(models.TextChoices):
    GOOD = "GOOD", "잘 먹었어요"
    BAD  = "BAD",  "별로였어요"


#세부 선택 옵션 
class DetailOption(models.Model):
    label = models.CharField(max_length=20)
    initial_label = models.CharField(max_length=30, choices=ReviewOption.choices, db_index=True)  # "잘 먹었어요" | "별로였어요"
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["initial_label", "sort_order", "id"]

    def __str__(self):
        return f"[{self.initial_label}] {self.label}"

#DB 저장용 로그 
class MealLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                            on_delete=models.SET_NULL, related_name="meal_logs")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    initial_label = models.CharField(max_length=30, choices=ReviewOption.choices)
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
    
# Create your models here.
class ReviewOption(models.Model):
    KIND = (("GOOD", "칭찬"), ("BAD", "불만"))
    key = models.SlugField(unique=True)                    # ex) liked_dish, too_salty
    label = models.CharField(max_length=30)               # 버튼에 보이는 텍스트 (ex. "간이 딱 맞아요")
    kind = models.CharField(max_length=4, choices=KIND)   # GOOD/BAD
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"[{self.kind}] {self.label}"


class MealReview(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="food_reviews"
    )
    restaurant = models.ForeignKey(
        "restaurants.Restaurant", on_delete=models.CASCADE, related_name="meal_reviews"
    )
    # 주문/회차 식별용
    order_code = models.CharField(max_length=50, blank=True, db_index=True)
    meal_feedback = models.CharField(max_length=50, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

'''
# DB 로그 기록 (수정 중)
class mealLog(models.Model):
    keyword = models.CharField(max_length=100)
    stage = models.CharField(max_length=20) # "잘 먹었어요" or "별로였어요"
    created_at = models.DateTimeField(auto_now_add=True)
'''

class MealReview(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="food_reviews"
    )
    restaurant = models.ForeignKey(
        "restaurants.Restaurant", on_delete=models.CASCADE, related_name="meal_reviews"
    )
    # 주문/회차 식별용
    order_code = models.CharField(max_length=50, blank=True, db_index=True)
    meal_feedback = models.CharField(max_length=50, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

'''
# DB 로그 기록 (수정 중)
class mealLog(models.Model):
    keyword = models.CharField(max_length=100)
    stage = models.CharField(max_length=20) # "잘 먹었어요" or "별로였어요"
    created_at = models.DateTimeField(auto_now_add=True)
'''