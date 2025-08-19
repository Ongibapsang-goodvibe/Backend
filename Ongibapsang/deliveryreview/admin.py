from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(DetailOption)
class DetailOptionAdmin(admin.ModelAdmin):
    list_display  = ("id","label", "initial_label", "sort_order")
    search_fields = ("label",)
    ordering      = ("initial_label", "sort_order", "id")


@admin.register(DeliveryLog)
class DeliveryLogAdmin(admin.ModelAdmin):
    list_display  = ("id", "initial_label", "option_label", "source", "created_at")
    list_filter   = ("initial_label", "source")
    search_fields = ("option_label", "text")
    date_hierarchy = "created_at"
    ordering      = ("-id",)