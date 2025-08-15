from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ("id","name","phone","district_name")
