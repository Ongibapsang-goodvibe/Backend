from rest_framework import serializers
from .models import *

#질환 시리얼라이저 
class UserDiseaseSerializer(serializers.ModelSerializer):
    # disease_id 배열로 받기
    disease_id = serializers.PrimaryKeyRelatedField(
        source="diseases",          # User.diseases M2M 필드와 연결
        queryset=Disease.objects.all(),
        many=True
    )

    class Meta:
        model = User
        fields = ["id", "disease_id"]

    def update(self, instance, validated_data):
        diseases = validated_data.pop("diseases", None)
        if diseases is not None:
            instance.diseases.set(diseases)   # 전체 교체
        return instance
    

# 유저 정보 시리얼라이저 
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "district_name"]
