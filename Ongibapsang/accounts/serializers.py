from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import *

#로그인 시리얼라이저
class LoginSerializer(serializers.Serializer):
    name=serializers.CharField()
    password=serializers.CharField(write_only=True)

    def validate(self, attrs):
        name = attrs.get("name")
        password = attrs.get("password")

        user = authenticate(username=name, password=password)
        if not user:
            raise serializers.ValidationError("이름 또는 비밀번호가 올바르지 않습니다.")
        attrs["user"] = user
        return attrs



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
