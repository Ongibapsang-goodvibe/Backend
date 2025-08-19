from rest_framework import serializers
from .models import *
from orders.models import Order


class DetailOptionSerializer(serializers.ModelSerializer):
    class Meta: 
        model = DetailOption
        fields = ["id", "label", "initial_label", "sort_order"]


class DeliveryLogSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(
        queryset = Order.objects.all(), required=True 
    ) #주문 항상 있어야 함
    option = serializers.PrimaryKeyRelatedField(
        queryset = DetailOption.objects.all(), required=False, allow_null=True
    )


    class Meta:
        model = DeliveryLog
        fields = ["id","initial_label","source","order","option","option_label","text","created_at"]
        read_only_fields = ["id","created_at"]

    def validate(self, attrs):
        init= attrs.get("initial_label")
        source = attrs.get("source") or Source.BUTTON
        option = attrs.get("option")
        option_label = (attrs.get("option_label") or "").strip()
        text = (attrs.get("text") or "").strip()

        #'네'를 택할 경우에 바로 저장
        if init==DeliveryOption.GOOD:
            if option and not option_label:
                attrs["option_label"] = option.label
            attrs["text"] = text
            attrs["option_label"] = attrs.get("option_label") or option_label
            return attrs

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
        