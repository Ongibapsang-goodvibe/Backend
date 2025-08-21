<<<<<<< HEAD
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
=======
# orders/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from orders.models import Order
from orders.serializers import MakeOrderSerializer, ReadOrderSerializer
from restaurants.recommendation import main_recommend

class MakeOrderView(generics.ListCreateAPIView):
    serializer_class = MakeOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("menu")
    
class DeleteOrderView(generics.DestroyAPIView):
    serializer_class = ReadOrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

class OrderListView(generics.ListAPIView):
    serializer_class = ReadOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("menu")
    
class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = ReadOrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("menu")

# 추천 메뉴 API
class RecommendAPIView(APIView):
    def get(self, request):
        user = request.user
        result = main_recommend(user, limit=10)
        return Response(result, status=status.HTTP_200_OK)
>>>>>>> origin/backup_0821
