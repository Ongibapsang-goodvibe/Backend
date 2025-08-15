from rest_framework import serializers
from .models import *


class ReviewOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewOption
        fields = ["id", "label", "sort_order"]



class DetailOptionSerializer(serializers.ModelSerializer):
    class Meta: 
        model = DetailOption
        fields = ["id", "label", "initial_label", "sort_order"]


class MealLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealLog
        fields = ["id","initial_label","source","option","option_label","text","created_at"]
        read_only_fields = ["id","created_at"]

    def validate(self, attrs):
        source = attrs.get("source") or Source.BUTTON
        option = attrs.get("option")
        option_label = (attrs.get("option_label") or "").strip()
        text = (attrs.get("text") or "").strip()

        if source == Source.BUTTON:
            if not option and not option_label:
                raise serializers.ValidationError("BUTTON은 option 또는 option_label 중 하나가 필요합니다.")
        elif source == Source.VOICE:
            if not text:
                raise serializers.ValidationError("VOICE는 text가 필요합니다.")
        else:
            raise serializers.ValidationError("잘못된 source")

        # option이 있으면 라벨 보정
        if option and not option_label:
            attrs["option_label"] = option.label

        # 공백만 들어오지 않게 정리
        attrs["text"] = text
        attrs["option_label"] = option_label
        return attrs
        