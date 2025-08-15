from django.db import models
from django.conf import settings

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


# DB 로그 기록 (수정 중)
class mealLog(models.Model):
    keyword = models.CharField(max_length=100)
    stage = models.CharField(max_length=20) # "잘 먹었어요" or "별로였어요"
    created_at = models.DateTimeField(auto_now_add=True)