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
    restaurant_request = models.CharField(max_length=250, blank=True, null=True)
    
    DELIVERY_REQUEST_CHOICES = [
        ("call", "도착하면 전화해주세요."),
        ("text", "도착하면 문자해주세요."),
        ("in_person", "직접 받을게요. (부재시 문 앞)"),
        ("bell", "문 앞에 놔주세요. (초인종 O)"),
        ("no_bell", "문 앞에 놔주세요. (초인종 X)")
    ]
    delivery_request = models.CharField(max_length=20, choices=DELIVERY_REQUEST_CHOICES, blank=True, null=True)

    PAYMENT_CHOICES = [
        ("cash", "만나서 현금결제"),
        ("card", "만나서 카드결제"),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user} | {self.menu} x {self.quantity} _ {self.time:%Y-%m-%d %H:%M}"
    
