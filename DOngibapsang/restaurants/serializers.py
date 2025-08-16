# restaurant/serializers.py
from rest_framework import serializers

class SearchInputSerializer(serializers.Serializer):
    text = serializers.CharField(required=False, allow_blank=False)
    transcription_id = serializers.IntegerField(required=False)
    limit = serializers.IntegerField(required=False, default=10)

    def validate(self, attrs):
        if not attrs.get("text") and not attrs.get("transcription_id"):
            raise serializers.ValidationError("text 또는 transcription_id 중 하나는 필요합니다.")
        return attrs

class MenuCardSerializer(serializers.Serializer):
    menu_id = serializers.IntegerField()
    menu_name = serializers.CharField()
    price = serializers.IntegerField(allow_null=True)
    restaurant_id = serializers.IntegerField()
    restaurant_name = serializers.CharField()  # ← 문자열이어야 함
    delivery_fee = serializers.IntegerField()
    image_url = serializers.CharField(allow_null=True)

 
