from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Order
from .serializers import MakeOrderSerializer, ReadOrderSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from restaurants.recommendation import main_recommend

# Create your views here.
class OrderListView(generics.ListCreateAPIView):
    permission_classes = [permissions.AllowAny]  # 개발 임시
    queryset = Order.objects.all()               # get_queryset 오버라이드도 가능

    def get_serializer_class(self):
        return MakeOrderSerializer if self.request.method == "POST" else ReadOrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("menu")


class MakeOrderView(generics.ListCreateAPIView):
    serializer_class = MakeOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("menu")
    
class DeleteOrderView(generics.DestroyAPIView):
    serializer_class = ReadOrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    lookup_field = "id"

    
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

