from django.contrib import admin
from .models import *

class MenuInline(admin.TabularInline):
    model = Menu
    extra = 1
    fields = ("name", "price", "ingredients", )
    filter_horizontal = ("ingredients", )

class MenuNutritionInline(admin.TabularInline):
    model = MenuNutrition
    extra = 1

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "delivery_fee", "district_name")
    search_fields = ("name", "phone", "address")
    inlines = [MenuInline]

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "restaurant","category","price")

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = ("id", "keyword", "stage", "created_at")

