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
