# restaurant/models.py
from django.db import models
from django.core.validators import RegexValidator

district_code_validator = RegexValidator(r'^\d{10}$', '행정/법정동 코드는 10자리 숫자여야 합니다.')

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=255)
    image = models.ImageField(upload_to='restaurant_images/', null=True, blank=True)
    tag = models.CharField(max_length=100)  # 소개 태그
    name_initials = models.CharField(max_length=100, db_index=True, blank=True, default="")
    delivery_fee = models.IntegerField(default=0)

    district_name = models.CharField(max_length=40, help_text="표시용 동명(예: 연희동)")
    district_code = models.CharField(
        max_length=10,
        validators=[district_code_validator],
        db_index=True,
        help_text="행정/법정동 10자리 코드(예: 1141061500)",
    )

    def __str__(self):
        return self.name

# 수정 필요 
class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Menu(models.Model):
    name = models.CharField(max_length=100)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="menus")
    name_initials = models.CharField(max_length=100, db_index=True, blank=True, default="")
    image = models.ImageField(upload_to='restaurant_images/', null=True, blank=True)
    price = models.IntegerField(default=0)

    ingredients = models.ManyToManyField(Ingredient, related_name="menus", blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="menus")

    def __str__(self):
        return f"{self.name} @ {self.restaurant.name}"

class SearchLog(models.Model):
    source_transcription = models.ForeignKey("voice.Transcription", on_delete=models.CASCADE, null=True, blank=True)
    keyword = models.CharField(max_length=100)
    stage = models.CharField(max_length=20)  # restaurant | menu | ingredient | fallback | none
    created_at = models.DateTimeField(auto_now_add=True)