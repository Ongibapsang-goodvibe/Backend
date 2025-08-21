from rest_framework import serializers
from .models import NutritionReport

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