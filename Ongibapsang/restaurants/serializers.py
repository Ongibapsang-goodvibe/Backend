# restaurant/serializers.py
from rest_framework import serializers
from .models import * 

class SearchInputSerializer(serializers.Serializer):
    text = serializers.CharField(required=True, allow_blank=False)
    limit = serializers.IntegerField(required=False, default=10)

# 메뉴 한 건을 카드 형태로 직렬화 
class MenuCardSerializer(serializers.ModelSerializer):
    menu_id = serializers.IntegerField(source="id", read_only=True)
    menu_name = serializers.CharField(source="name", read_only=True)
    price = serializers.IntegerField(allow_null=True)
    restaurant_id = serializers.IntegerField(source="restaurant.id", read_only=True)
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)
    delivery_fee = serializers.IntegerField(source="restaurant.delivery_fee", read_only=True)
    delivery_time = serializers.IntegerField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ["menu_id", "menu_name", "price", "restaurant_id", "restaurant_name", "delivery_fee", "image_url"]

    def get_image_url(self, obj):
        img = getattr(obj, "image", None)
        return img.url if img else None

