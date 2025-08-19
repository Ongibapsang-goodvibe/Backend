from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ("id","name")