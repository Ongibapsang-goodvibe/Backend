from rest_framework import serializers

class NutritionReportSerializer(serializers.Serializer):
    disease = serializers.CharField()
    nutrient = serializers.CharField()
    total_week = serializers.FloatField()
    