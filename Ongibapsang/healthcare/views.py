from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework import generics
from .models import *
from .serializers import *

# Create your views here.

#DB 저장용
class HealthcareLogView(generics.CreateAPIView):
    serializer_class=HealthcareLogSerializer
    permission_classes=[AllowAny]
    parser_classes=[JSONParser, FormParser, MultiPartParser] #JSON/폼 다 받기

