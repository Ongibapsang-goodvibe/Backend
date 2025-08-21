from rest_framework import serializers
from orders.models import Order
from restaurants.models import Menu, MenuNutrition
from collections import defaultdict

class MakeOrderSerializer(serializers.ModelSerializer):
    menu_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Menu.objects.all(), source="menu"
    )

    class Meta:
        model = Order
        fields = ("id", "menu_id", "quantity", "time")
<<<<<<< HEAD
        read_only_fields = ("id", "time")

    def create(self, validated_data):
        user = self.context["request"].user
        order = Order(user=user, **validated_data)
        
        # 고정 기록 생성, 메뉴에 있는 영양소를 기록
        nmap = {}
        for mn in order.menu.menu_nutritions.select_related("nutrient").all():  # ✅ 올바른 접근
            if not mn.nutrient or mn.amount is None:
                  continue
        code = mn.nutrient.code or mn.nutrient.name
        nmap[code] = float(mn.amount)
        order.record_fixed = nmap
        order.save()
=======

    def create(self, validated_data):
        user = self.context["request"].user
        menu = validated_data["menu"]
        quantity = validated_data.get("quantity", 1)
        order = Order(user=user, **validated_data)
        
        # 고정 기록 생성, 메뉴에 있는 영양소를 기록
        def _to_grams(value: float, unit: str | None) -> float:
            """질량/부피 단위를 g로 통일"""
            if value is None:
                return 0.0
            if not unit:
                return float(value)
            u = unit.lower()
            if u == "g":
                return float(value)
            if u == "mg":
                return float(value) / 1000.0
            if u in ("µg", "μg", "ug"):
                return float(value) / 1_000_000.0
            if u == "ml":
                return float(value)
            if u == "kcal":
                return float(value)
            return float(value)
        
        def _menu_nutrients_g(menu: Menu) -> tuple[dict]:
            grams = defaultdict(float)

            for mn in menu.menu_nutritions.all():
                code = mn.nutrient.code  # pk 기반이면 id도 가능
                unit = mn.nutrient.unit or ""
                val = float(mn.amount)
                grams[code] += _to_grams(val, unit)
            return dict(grams)
        
        grams = _menu_nutrients_g(menu)

        menu_price = int(menu.price)
        delivery_fee = int(menu.restaurant.delivery_fee)
        total_price = (menu_price + delivery_fee) * quantity

        order = Order.objects.create(
            user=user,
            menu=menu,
            quantity=quantity,
            menu_price=menu_price,
            delivery_fee=delivery_fee,
            total_price=total_price,
            record_fixed=grams
        )
>>>>>>> origin/backup_0821
        return order

class ReadOrderSerializer(serializers.ModelSerializer):
    menu_name = serializers.CharField(source="menu.name", read_only=True)
    restaurant_name = serializers.CharField(source="menu.restaurant.name", read_only=True)

    class Meta:
        model = Order
        fields = ("id", "restaurant_name", "menu_name", "quantity", "total_price", "time", "record_fixed")
