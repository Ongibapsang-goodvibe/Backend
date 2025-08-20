# restaurants/admin.py
from django.contrib import admin
from .models import Restaurant, Menu, Ingredient, SearchLog

class MenuInline(admin.TabularInline):
    model = Menu
    extra = 1
    fields = ("name", "price", "ingredients", )
    filter_horizontal = ("ingredients", )

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

