from django.contrib import admin
from restaurants.models import *

# Register your models here.
admin.site.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant')
    filter_horizontal = ('ingredients', 'tags')

admin.site.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'district_name')


admin.site.register(Tag)
admin.site.register(Ingredient)

