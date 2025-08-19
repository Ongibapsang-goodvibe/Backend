# orders/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from orders.serializers import MakeOrderSerializer, ReadOrderSerializer
from restaurants.recommendation import main_recommend


# ---------------------
# 주문 조회 / 생성
# ---------------------
class OrderListView(generics.ListCreateAPIView):
    """
    GET: 내 주문 목록 조회
    POST: 메뉴 선택 후 주문 생성
    """
    serializer_class = MakeOrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("menu")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ReadOrderSerializer
        return MakeOrderSerializer

# 추천 메뉴 API
class RecommendAPIView(APIView):
    """
    GET: 최근 7일간 주문 + 질환 규칙 기반 추천 메뉴
    """
    def get(self, request):
        user = request.user
        result = main_recommend(user, limit=10)
        return Response(result, status=status.HTTP_200_OK)
