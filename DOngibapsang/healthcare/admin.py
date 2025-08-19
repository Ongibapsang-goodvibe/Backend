from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(DiseaseRules)
class DiseaseRulesAdmin(admin.ModelAdmin):
    list_display = ("id", "disease", "nutrient", "min_week", "max_week")
    list_filter = ("disease", "nutrient")  