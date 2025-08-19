from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Order
from .serializers import MakeOrderSerializer, ReadOrderSerializer

# Create your views here.
# 유저 인증에서 500 에러 떠서 임시로 수정함(현재는 AllowAny 기준) 
class OrderListView(generics.ListCreateAPIView):
    permission_classes = [permissions.AllowAny]  # 개발 임시
    queryset = Order.objects.all()               # get_queryset 오버라이드도 가능

    def get_serializer_class(self):
        return MakeOrderSerializer if self.request.method == "POST" else ReadOrderSerializer

    def perform_create(self, serializer):
        # 여기서 예외가 터지면 runserver 콘솔에 트레이스백이 나옵니다.
        serializer.save()
