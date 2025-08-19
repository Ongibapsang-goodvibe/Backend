from rest_framework import serializers
from .models import User
from healthcare.models import Disease

class UserDiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = ("id", "name")

class UserSerializer(serializers.ModelSerializer):
    diseases = UserDiseaseSerializer(many=True, read_only=True)
    disease_ids = serializers.PrimaryKeyRelatedField(many=True, write_only=True, queryset=Disease.objects.all(), source="disease")

    class Meta:
        model = User
        fields = ("id", "username", "email", "diseases", "disease_ids")