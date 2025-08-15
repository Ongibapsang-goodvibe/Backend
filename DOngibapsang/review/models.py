from django.db import models
from django.conf import settings

# Create your models here.
# 식사/배달 평가 
class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="reviews"
    )
    restaurant = models.ForeignKey(
        "restaurants.Restaurant", on_delete=models.CASCADE, related_name="reviews"
    )
    # 주문/회차 식별용
    order_code = models.CharField(max_length=50, blank=True, db_index=True)
    meal_feedback = models.CharField(max_length=50, blank=True, db_index=True)
    delivery_feedback = models.CharField(max_length=50, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)