from django.contrib import admin
from chat.models import *

# Register your models here.
@admin.register(ChatMessage)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("id", "role", "content","created_at")