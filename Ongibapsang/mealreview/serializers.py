from rest_framework import serializers
from .models import *
from orders.models import Order


class DetailOptionSerializer(serializers.ModelSerializer):
    class Meta: 
        model = DetailOption
        fields = ["id", "label", "initial_label", "sort_order"]


class MealLogSerializer(serializers.ModelSerializer):
    # FK들을 명시적으로 지정 (권장)
    order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), required=True  # 주문이 항상 있어야 하면 True
    )
    option = serializers.PrimaryKeyRelatedField(
        queryset=DetailOption.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = MealLog
        fields = ["id","initial_label","order","source","option","option_label","text","created_at"]
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

        attrs["text"] = text
        attrs["option_label"] = option_label
        return attrs
    

    #리뷰 집계용
    def create(self, validated_data):
        return self.Meta.model.objects.create(**validated_data)