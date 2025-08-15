from django.db import models
from django.core.validators import RegexValidator

district_code_validator = RegexValidator(r'^\d{10}$', '행정/법정동 코드는 10자리 숫자여야 합니다.')

# Create your models here.
class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=255)
    image = models.ImageField(upload_to='restaurant_images/', null=True, blank=True) # 가게 사진 
    tag = models.CharField(max_length=100) # 소개 태그
    name_initials = models.CharField(max_length=100, db_index=True, blank=True, default="")  #초성 검색 

    district_name = models.CharField(
        max_length=40,
        help_text="표시용 동명(예: 연희동)"
    )

    district_code = models.CharField(
        max_length=10,
        validators=[district_code_validator],
        db_index=True,                 # 필터링 성능 ↑
        help_text="행정/법정동 10자리 코드(예: 1141061500)"
    )

    def __str__(self):
        return self.name
    
class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)  # 예: "매운", "비건", "알레르겐-땅콩"

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=50, unique=True)  # 예: "두부"

    def __str__(self):
        return self.name


class IngredientAlias(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="aliases")
    text = models.CharField(max_length=50, unique=True, db_index=True)  # 예: "순두부", "豆腐", "비지"



class Menu(models.Model):
    name = models.CharField(max_length=100)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="menus")  # ← IntegerField 대신 FK
    name_initials = models.CharField(max_length=100, db_index=True, blank=True, default="")
    image = models.ImageField(upload_to='restaurant_images/', null=True, blank=True)

    ingredients = models.ManyToManyField(Ingredient, related_name="menus", blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="menus") # 예: "매운", 

    def __str__(self):
        return f"{self.name}({self.restaurant.name})"
