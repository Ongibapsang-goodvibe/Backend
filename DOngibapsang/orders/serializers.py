from rest_framework import serializers
from .models import Order
from restaurants.models import Menu

class MakeOrderSerializer(serializers.ModelSerializer):
    menu_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Menu.objects.all(), source="menu"
    )

    class Meta:
        model = Order
        fields = ("id", "menu_id", "quantity", "time")

    def create(self, validated_data):
        user = self.context["request"].user
        order = Order(user=user, **validated_data)
        
        # 고정 기록 생성, 메뉴에 있는 영양소를 기록
        nmap = {}
        for mn in order.menu.menu_nutritions.all():
            code = mn.nutrient.code or mn.nutrient.name
            nmap[code] = float(mn.amount)
        order.record_fixed = nmap
        order.save()
        return order

class ReadOrderSerializer(serializers.ModelSerializer):
    menu_name = serializers.CharField(source="menu.name", read_only=True)

    class Meta:
        model = Order
        fields = ("id", "menu_name", "quantity", "time", "record_fixed")
