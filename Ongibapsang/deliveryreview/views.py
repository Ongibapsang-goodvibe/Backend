from django.shortcuts import render
import json
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
        init = self.request.query_params.get("initial_label")
        qs = DetailOption.objects.order_by("initial_label", "sort_order", "id")
        return qs.filter(initial_label=init) if init else qs.none()
    

#DB 저장용
class DeliveryLogView(generics.CreateAPIView):
    serializer_class=DeliveryLogSerializer
    permission_classes=[AllowAny]
    parser_classes=[JSONParser, FormParser, MultiPartParser] #JSON/폼 다 받기

