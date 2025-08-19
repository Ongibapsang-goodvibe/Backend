# restaurant/serializers.py
from rest_framework import serializers
from .models import * 

class SearchInputSerializer(serializers.Serializer):
    text = serializers.CharField(required=True, allow_blank=False)
    # transcription_id = serializers.IntegerField(required=False)
    limit = serializers.IntegerField(required=False, default=10)

    # def validate(self, attrs):
    #     if not attrs.get("text") and not attrs.get("transcription_id"):
    #         raise serializers.ValidationError("text 또는 transcription_id 중 하나는 필요합니다.")
    #     return attrs

# 서치 결과 메뉴 카트 시리얼라이저
class MenuCardSerializer(serializers.ModelSerializer):
    menu_id = serializers.IntegerField(source="id", read_only=True)
    menu_name = serializers.CharField(source="name", read_only=True)
    restaurant_id = serializers.IntegerField(source="restaurant.id", read_only=True)
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)
    delivery_fee = serializers.IntegerField(source="restaurant.delivery_fee", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ["menu_id", "menu_name", "price", "restaurant_id", "restaurant_name", "delivery_fee", "image_url"]

    def get_image_url(self, obj):
        img = getattr(obj, "image", None)
        return img.url if img else None

