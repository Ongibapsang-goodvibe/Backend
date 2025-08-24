from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Order
from .serializers import *
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from restaurants.recommendation import main_recommend
from django.utils import timezone
from datetime import timedelta
from django.utils.formats import date_format
from django.shortcuts import get_object_or_404
from restaurants.models import * 

# Create your views here.
class OrderListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated] 
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


#결제 금액, 배달 시간 계산
class OrderOutputView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = MenuInputSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        restaurant = get_object_or_404(Restaurant, pk=s.validated_data["restaurant_id"])
        menu = get_object_or_404(Menu, pk=s.validated_data["menu_id"])
        qty = int(s.validated_data.get("qty", 1))

        # 같은 식당 메뉴인지 검증
        if menu.restaurant_id != restaurant.id:
            return Response({"detail": "해당 식당의 메뉴가 아닙니다."}, status=400)
        
        #입력값 가져오기
        restaurant_request = s.validated_data.get("restaurant_request", "")
        delivery_request = s.validated_data.get("delivery_request", "")
        payment_method = s.validated_data["payment_method"]

        # 금액 계산
        subtotal = menu.price * qty
        delivery_fee = restaurant.delivery_fee or 0
        small_order_fee = 500 if subtotal < 10000 else 0
        total = subtotal + delivery_fee + small_order_fee

        # ETA 계산
        now = timezone.localtime(timezone.now())
        eta_minutes = int(getattr(restaurant, "delivery_time", 0) or 0)
        eta_dt = now + timedelta(minutes=eta_minutes)
        eta_text = date_format(eta_dt, "H시 i분")  # 예: "12시 30분"

        out = OutputSerializer({
            "order_amount": subtotal,
            "delivery_fee": delivery_fee,
            "small_order_fee": small_order_fee,
            "total": total,
            "ordered_at": now,
            "eta_minutes": eta_minutes,
            "eta_at": eta_dt,
            "eta_text": eta_text,
            "restaurant_request": restaurant_request,
            "delivery_request": delivery_request,
            "payment_method": payment_method,
        }).data
        return Response(out, status=status.HTTP_200_OK)