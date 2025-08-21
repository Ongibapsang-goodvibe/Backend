from rest_framework import serializers
from .models import *

# healthcare 저장 로그 시리얼라이저 
class HealthcareLogSerializer(serializers.ModelSerializer):
    #order = serializers.PrimaryKeyRelatedField(queryset = Order.objects.all(), required=True)
    order = serializers.IntegerField(source="order_id", read_only=True)

    class Meta:
        model = HealthcareLog
        fields = ["id", "initial_label", "order", "text", "mood_label", "created_at"]
        read_only_fields = ["id", "created_at"]

    
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
    bad_count = serializers.IntegerField()
    bad_logs = HealthcareLogSerializer(many=True)
    dominant_mood = serializers.CharField()
    mood_counts = serializers.DictField(child=serializers.IntegerField())
