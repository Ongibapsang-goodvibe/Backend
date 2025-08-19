from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import RegexValidator
from healthcare.models import Disease


# Create your models here.
# 어르신 사용자 모델
class User(AbstractUser):
    username = models.CharField(max_length=100, null=True, blank=True) 
    phone = models.CharField(max_length=20, unique=True)  
    district_name = models.CharField(max_length=40, help_text="표시용 동명(예: 연희동)", null=True, blank=True)
    district_code = models.CharField(max_length=10, default=0)

    diseases = models.ManyToManyField(
        Disease,
        related_name="users",
        blank=True,
        help_text="사용자가 보유한 질환"
    )

    USERNAME_FIELD = 'phone' 
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username 



