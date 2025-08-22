from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework import generics
from .models import *
from .serializers import * 

# Create your views here.
class DetailOptionView(generics.ListAPIView):
    serializer_class = DetailOptionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        init = self.request.query_params.get("kind")
        qs = DetailOption.objects.order_by("kind", "sort_order", "id")
        return qs.filter(kind=init) if init else qs.none()

# DB 저장용 
class MealLogView(generics.CreateAPIView):
    serializer_class = MealLogSerializer
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser] 

    #리뷰 작성자 유저 정보 저장 
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

#리뷰 조회용
class MenuReviewSummary(generics.ListCreateAPIView):
    serializer_class = MealLogSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        menu_id = self.request.query_params.get("menu")
        qs = MealLog.objects.all()
        if menu_id:
            qs = qs.filter(order__menu_id=menu_id)
        source = self.request.query_params.get("source")
        if source:
            qs = qs.filter(source=source)
        return qs.select_related("order", "user").order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
