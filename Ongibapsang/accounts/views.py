from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import generics, permissions
from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from .models import User
from .serializers import UserSerializer

# Create your views here.
# 로그인(이름+비밀번호 숫자 6자리) 
class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.validated_data["user"]

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user": {
                "id": user.id,
                "name": user.username,  # username 필드에 이름 저장했다고 가정
            }
        }, status=status.HTTP_200_OK)
    

#로그아웃
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # 토큰 필요

    def post(self, request):
        # 현재 요청에 사용된 토큰 객체가 있으면 삭제
        if getattr(request, "auth", None):
            request.auth.delete()  # Token row 삭제 -> 즉시 무효화
        return Response(status=status.HTTP_204_NO_CONTENT)



User = get_user_model()
#질환 처음 저장 
# views.py
class DiseaseUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserDiseaseSerializer
    permission_classes = [AllowAny]   # 로그인 가정이면 IsAuthenticated

   
class UserView(APIView):
    permission_classes = [AllowAny] 

    def get(self, request):
        serializers = UserSerializer(request.user)
        return Response(serializers.data)
