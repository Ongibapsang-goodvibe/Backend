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
        fields = ("id", "menu_id", "restaurant_request", "delivery_request", "payment_method", "quantity", "time")
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

        # 모델에 필드가 있을 때만 세팅
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
    price = serializers.IntegerField(source="menu.price", read_only=True)
    delivery_fee = serializers.IntegerField(source="menu.restaurant.delivery_fee", read_only=True)
    delivery_time = serializers.IntegerField(source="menu.restaurant.delivery_time", read_only=True)
    small_order_fee = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ("id", "restaurant_name", "menu_name", "quantity", "price", "delivery_fee", "delivery_time", "small_order_fee", "total_price", "time", "record_fixed",)

    def get_small_order_fee(self, obj):
        menu_price = int(getattr(obj.menu, "price", 0) or 0)
        subtotal = menu_price * (obj.quantity or 1)
        return 500 if subtotal < 10000 else 0

    def get_total_price(self, obj):
        menu_price = int(getattr(obj.menu, "price", 0) or 0)
        delivery_fee = int(getattr(obj.menu.restaurant, "delivery_fee", 0) or 0)
        qty = int(getattr(obj, "quantity", 1) or 1)
        small_order_fee = self.get_small_order_fee(obj)
        return (menu_price * qty) + delivery_fee + small_order_fee


#결제 금액, 배달 시간 계산용 시리얼라이저 
class MenuInputSerializer(serializers.Serializer):
    restaurant_id = serializers.IntegerField()
    menu_id = serializers.IntegerField()
    qty = serializers.IntegerField(min_value=1, default=1, required=False)  # 옵션
    restaurant_request = serializers.CharField(required=False, allow_blank=True)
    delivery_request = serializers.ChoiceField(choices=Order.DELIVERY_REQUEST_CHOICES, required=False)
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_CHOICES, required=True)


class OutputSerializer(serializers.Serializer):
    order_amount = serializers.IntegerField()
    delivery_fee = serializers.IntegerField()
    small_order_fee = serializers.IntegerField()
    total = serializers.IntegerField()
    ordered_at = serializers.DateTimeField()
    eta_minutes = serializers.IntegerField()
    eta_at = serializers.DateTimeField()
    eta_text = serializers.CharField()