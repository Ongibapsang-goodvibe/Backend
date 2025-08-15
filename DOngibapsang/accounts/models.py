from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
# 어르신 사용자 모델 기준
class User(AbstractUser):
    username = models.CharField(max_length=100, null=True, blank=True) 
    phone = models.CharField(max_length=20, unique=True)  
    token = models.CharField(max_length=20, unique=True)  
    coupon = models.PositiveIntegerField(default=5)
    district_name = models.CharField(max_length=40, null=True, blank=True)   # 예: '연희동'
    district_code = models.CharField(max_length=10, null=True, blank=True, db_index=True)  # 법정/행정동 코드(10자리 권장)

    # 인증 기준 필드 변경
    USERNAME_FIELD = 'token' #복지관 코드로 인증 
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username 


# 주문 기록
class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  
        null=True, blank=True,
        related_name="orders",
    )
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.PROTECT,   
        related_name="orders",
    )
    menu = models.ForeignKey(
        "restaurants.Menu",
        on_delete=models.PROTECT,    
        related_name="orders",
    )
    ordered_at = models.DateTimeField(auto_now_add=True, db_index=True)
