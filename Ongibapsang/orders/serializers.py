from collections import defaultdict
from typing import Type

from django.db import models
from django.db.models import Model
from rest_framework import serializers

from orders.models import Order
from restaurants.models import Menu


class MakeOrderSerializer(serializers.ModelSerializer):
    menu_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Menu.objects.all(), source="menu"
    )

    class Meta:
        model = Order
        fields = ("id", "menu_id", "quantity", "time")
        read_only_fields = ("id", "time")

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        menu: Menu = validated_data["menu"]
        quantity = int(validated_data.get("quantity", 1) or 1)

        # ---- 단위 통일 ----
        def _to_grams(value: float | int | None, unit: str | None) -> float:
            if value is None:
                return 0.0
            v = float(value)
            if not unit:
                return v
            u = unit.lower()
            if u == "g":
                return v
            if u == "mg":
                return v / 1000.0
            if u in ("µg", "μg", "ug"):
                return v / 1_000_000.0
            return v  # ml, kcal 등은 그대로

        grams = defaultdict(float)
        for mn in menu.menu_nutritions.select_related("nutrient").all():
            nutrient = getattr(mn, "nutrient", None)
            amount = getattr(mn, "amount", None)
            if not nutrient or amount is None:
                continue
            code = getattr(nutrient, "code", None) or getattr(nutrient, "name", None)
            unit = getattr(nutrient, "unit", "") or ""
            grams[code] += _to_grams(amount, unit)

        if quantity != 1:
            for k in list(grams.keys()):
                grams[k] *= quantity
        record_fixed = dict(grams)

        # ---- 모델에 필드가 있을 때만 세팅 ----
        def _has_field(model_cls: Type[Model], field_name: str) -> bool:
            try:
                model_cls._meta.get_field(field_name)
                return True
            except Exception:
                return False

        create_kwargs = {
            "user": user,
            "menu": menu,
            "quantity": quantity,
            "record_fixed": record_fixed,
        }

        if _has_field(Order, "menu_price"):
            create_kwargs["menu_price"] = int(getattr(menu, "price", 0) or 0)
        if _has_field(Order, "delivery_fee"):
            create_kwargs["delivery_fee"] = int(getattr(menu.restaurant, "delivery_fee", 0) or 0)
        if _has_field(Order, "total_price"):
            mp = int(getattr(menu, "price", 0) or 0)
            df = int(getattr(menu.restaurant, "delivery_fee", 0) or 0)
            create_kwargs["total_price"] = (mp + df) * quantity

        return Order.objects.create(**create_kwargs)


class ReadOrderSerializer(serializers.ModelSerializer):
    menu_name = serializers.CharField(source="menu.name", read_only=True)
    restaurant_name = serializers.CharField(source="menu.restaurant.name", read_only=True)
    # total_price가 모델에 없을 수도 있으니 보호용(선택)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ("id", "restaurant_name", "menu_name", "quantity", "total_price", "time", "record_fixed")

    def get_total_price(self, obj):
        # 모델 필드가 있으면 그대로, 없으면 계산해서 리턴
        if hasattr(obj, "total_price") and obj.total_price is not None:
            return obj.total_price
        mp = int(getattr(obj.menu, "price", 0) or 0)
        df = int(getattr(obj.menu.restaurant, "delivery_fee", 0) or 0)
        qty = int(getattr(obj, "quantity", 1) or 1)
        return (mp + df) * qty
