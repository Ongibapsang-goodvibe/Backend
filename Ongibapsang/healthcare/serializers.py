from rest_framework import serializers
from .models import *
from orders.models import Order

# healthcare 저장 로그 시리얼라이저 
class HealthcareLogSerializer(serializers.ModelSerializer):
    '''order = serializers.PrimaryKeyRelatedField(
        queryset = Order.objects.all(), required=True
    )'''
    order = serializers.IntegerField(write_only=True)  # int ID로 받기
    order_id = serializers.SerializerMethodField(read_only=True)  # 응답 시 ID 그대로 보여주기

    class Meta:
        model = HealthcareLog
        fields = ["id", "initial_label", "order", "order_id", "text", "mood_label", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_order_id(self, obj):
        return obj.order.id if obj.order else None

    
    def validate(self, attrs):
        init = attrs.get("initial_label")
        text = (attrs.get("text") or "").strip()
        mood = attrs.get("mood_label")

        # '아무 문제 없어요' 선택 시 바로 저장 
        if init == HealthcareOption.GOOD:
            attrs["text"] = ""
            return attrs

        # '어딘가 불편해요' 선택 시 음성 텍스트 저장 
        if init == HealthcareOption.BAD:
            attrs["text"] = text
            return attrs
        return attrs
    
    def create(self, validated_data):
        order_id = validated_data.pop("order", None)
        if order_id:
            try:
                validated_data["order"] = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                raise serializers.ValidationError({"order": f"Invalid order ID: {order_id}"})
        return super().create(validated_data)

class NutritionReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionReport
        field = ("id", "user", "disease", "date")
        read_only_fields = ("id", "user", "disease", "date")

class N_AnalysisSerializer(serializers.Serializer):
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    order_count = serializers.IntegerField()
    total_kcal = serializers.FloatField()
    total_g = serializers.DictField(child=serializers.FloatField())
    nutrient_percent = serializers.JSONField()
    weekly_recommend = serializers.DictField()
    ai_feedback = serializers.CharField()

class H_AnalysisSerializer(serializers.Serializer):
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    weekday_bad_texts = serializers.DictField()
    bad_count = serializers.IntegerField()
    bad_logs = HealthcareLogSerializer(many=True)
    dominant_mood = serializers.CharField()
    weekday_moods = serializers.DictField(child=serializers.IntegerField())
