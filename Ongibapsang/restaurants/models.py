# restaurant/models.py
from django.db import models
from django.core.validators import RegexValidator


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=255)
    image = models.ImageField(upload_to='restaurant_images/', null=True, blank=True)
    # name_initials = models.CharField(max_length=100, db_index=True, blank=True, default="")
    delivery_fee = models.IntegerField(default=0)

    district_name = models.CharField(max_length=40, help_text="표시용 동명(예: 연희동)")
    district_code = models.CharField(max_length=10, default=0)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Nutrient(models.Model):
    #영양소 별 고유 코드
    code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=50)
    unit = models.CharField(max_length=10, help_text="g, mg, µg, ml", null=True)

    def __str__(self):
        return f"{self.name}({self.unit})"
    

class MenuNutrition(models.Model):
    #메뉴 1회 제공량 기준 영양성분
    menu = models.ForeignKey("restaurants.Menu", on_delete=models.CASCADE, related_name="menu_nutritions")
    nutrient = models.ForeignKey("restaurants.Nutrient", on_delete=models.CASCADE, related_name="menu_values")
    amount = models.FloatField(help_text="해당 메뉴 1회분의 영양소 함량")

    class Meta:
        unique_together = ("menu", "nutrient")

    def __str__(self):
        return f"{self.menu.name} | {self.nutrient.name} : {self.amount}{self.nutrient.unit}"



class Menu(models.Model):
    CATEGORY_CHOICES = (
        (0, '국 · 찌개'),
        (1, '밥'),
        (2, '죽'),
        (3, '반찬')
    )
    name = models.CharField(max_length=100)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="menus")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default=0) 
    # name_initials = models.CharField(max_length=100, db_index=True, blank=True, default="")
    image = models.ImageField(upload_to='restaurant_images/', null=True, blank=True)
    price = models.IntegerField(default=0)


    ingredients = models.ManyToManyField(Ingredient, related_name="menus", blank=True)

    def __str__(self):
        return f"{self.name} @ {self.restaurant.name}"


class SearchLog(models.Model):
    text = models.TextField(blank=True, null=True, default="")
    keyword = models.CharField(max_length=100)
    stage = models.CharField(max_length=20)  # restaurant | menu | ingredient | fallback | none
    created_at = models.DateTimeField(auto_now_add=True)


