from django.shortcuts import render
import json
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework import generics
from .models import *
from .serializers import * 

# Create your views here.
class ReviewOptionView(generics.ListAPIView):
    serializer_class = ReviewOptionSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        return ReviewOption.objects.order_by("sort_order", "id")
        
    

class DetailOptionView(generics.ListAPIView):
    serializer_class = DetailOptionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        init = self.request.query_params.get("initial_label")
        qs = DetailOption.objects.filter(is_active=True)
        return qs.filter(initial_label=init) if init else qs.none()


# DB 저장용 
class MealLogView(generics.CreateAPIView):
    serializer_class = MealLogSerializer
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]  # ← JSON/폼 다 받기


def mealreview_test_page(request):
    """
    테스트 페이지용: DB의 DetailOption을 가져와 템플릿에 JSON으로 주입.
    '잘 먹었어요' / '별로였어요' 버튼은 템플릿에서 하드코딩.
    """
    mapping = {}
    for opt in DetailOption.objects.filter(is_active=True).order_by("initial_label", "sort_order", "id"):
        mapping.setdefault(opt.initial_label, []).append({"id": opt.id, "label": opt.label})
    return render(request, "mealreview/test.html", {
        "options_json": json.dumps(mapping, ensure_ascii=False)
    })