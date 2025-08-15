# restaurants/admin.py
from django.contrib import admin
from .models import Restaurant, Menu, Ingredient, Tag, SearchLog

class MenuInline(admin.TabularInline):
    model = Menu
    extra = 1
    fields = ("name", "price", "ingredients", "tags")
    filter_horizontal = ("ingredients", "tags")

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "delivery_fee", "district_name")
    search_fields = ("name", "phone", "address")
    inlines = [MenuInline]

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "restaurant", "price")
    search_fields = ("name",)
    list_filter = ("restaurant",)
    filter_horizontal = ("ingredients", "tags")

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = ("id", "keyword", "stage", "created_at")
    list_filter = ("stage",)
    search_fields = ("keyword",)
