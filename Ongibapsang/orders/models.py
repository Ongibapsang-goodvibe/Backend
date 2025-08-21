from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    menu = models.ForeignKey("restaurants.Menu", on_delete=models.CASCADE, related_name="orders")
    quantity = models.PositiveIntegerField(default=1)
    time = models.DateTimeField(default=timezone.now, db_index=True)
    record_fixed = models.JSONField(default=dict, blank=True)#JSON으로 주문 기록 저장 -> 나중에 같은 메뉴의 데이터가 변경되더라도 과거의 값은 유지
    total_price = models.IntegerField(default=0)
    menu_price = models.IntegerField(default=0)
    delivery_fee = models.IntegerField(default=0)
    quantity = models.PositiveIntegerField(default=1)
   
    def __str__(self):
        return f"{self.user} | {self.menu} x {self.quantity} _ {self.time:%Y-%m-%d %H:%M}"