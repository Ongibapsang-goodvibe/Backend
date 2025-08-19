from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display=("id", "username","district_name","display_diseases" )
    
    #disease 
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # M2M N+1 쿼리 방지
        return qs.prefetch_related("diseases")


    def display_diseases(self, obj):
        names = [d.name for d in obj.diseases.all()]
        return names