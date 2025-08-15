from rest_framework import serializers
from .models import *

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class MenuSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Menu
        fields = '__all__'

class RestaurantSerializer(serializers.ModelSerializer):
    menus = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = [
            'id','name','phone','address','image','tag','name_initials',
            'district_name','district_code','menus'
        ]

    def get_menus(self, obj):
        qs = getattr(obj, 'filtered_menus', None)
        return MenuSerializer(qs if qs is not None else obj.menus.all(), many=True).data