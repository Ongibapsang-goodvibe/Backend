from django.contrib import admin
from .models import *

@admin.register(ReviewOption)
class ReviewOptionAdmin(admin.ModelAdmin):
    ordering = ("kind", "sort_order", "id")
    list_display = ("id", "kind", "label", "sort_order", "is_active")
    list_filter = ("kind", "is_active")
    search_fields = ("label", "key") 


@admin.register(DetailOption)
class DetailOptionAdmin(admin.ModelAdmin):
    ordering = ("kind", "sort_order", "id")
    list_display = ("id", "initial_label_col", "label", "sort_order", "is_active")
    list_filter = ("kind", "is_active")
    search_fields = ("label", "key")

    def initial_label_col(self, obj):
        return obj.initial_label
    initial_label_col.short_description = "initial_label(호환)"


@admin.register(MealLog)
class MealLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "order", "initial_label", "source", "option_label", "created_at")
    list_filter = ("initial_label", "source", "created_at")
    search_fields = ("option_label", "text")  
    ordering = ("-created_at", "id")