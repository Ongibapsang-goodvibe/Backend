from django.contrib import admin
from .models import Order

# Register your models here.

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "menu", "quantity", "time")
    list_filter = ("time", "user")
    search_fields = ("menu__name", "user__username")


