import openai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, filters, generics #DRF의 SearchFilter
from .models import *
from .serializers import *
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend #django-filter
from django.conf import settings
from django.db.models import Q, Prefetch

openai.api_key = settings.OPENAI_API_KEY

audio_file_path = "C:/Users/samsung/Downloads/voice_test.mp3"

# Create your views here.
class MenuListView(generics.ListAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'restaurant', 'name_initials','ingredients','tags']

class RestaurantListView(generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'address', 'tag', 'name_initials','menus_name'] #역참조 필드명 menus -> 메뉴로 검색 가능

class TextSearchView(APIView):
    def post(self, request):
        search_text = request.data.get("text", "").strip()
        if not search_text:
            return Response({"error": "검색어가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 1) 식당 필드에서 검색
        restaurant_match = Restaurant.objects.filter(
            Q(name__icontains=search_text) |
            Q(address__icontains=search_text) |
            Q(tag__icontains=search_text)
        )

        # 2) 메뉴 필드에서 검색
        menu_match = Menu.objects.filter(
            Q(name__icontains=search_text) |
            Q(name_initials__icontains=search_text) |
            Q(ingredients__name__icontains=search_text) |
            Q(tags__name__icontains=search_text)
        ).distinct()
        """
        results = Restaurant.objects.filter(
            Q(name__icontains=search_text) |
            Q(address__icontains=search_text) |
            Q(tag__icontains=search_text) |
            Q(menus__name__icontains=search_text) |
            Q(menus__name_initials__icontains=search_text) |
            Q(menus__ingredients__name__icontains=search_text) |
            Q(menus__tags__name__icontains=search_text)
        ).distinct()
        """
        if restaurant_match.exists() and not menu_match.exists():
            # CASE 1: 식당만 검색된 경우 → 식당 정보 + 해당 식당의 모든 메뉴
            results = restaurant_match.prefetch_related('menus')
            serializer = RestaurantSerializer(results, many=True, context={'request': request})
            return Response({
                "search_text": search_text,
                "type": "restaurant",
                "results": serializer.data
            })

        elif menu_match.exists():
            # CASE 2: 메뉴가 검색된 경우 → 해당 메뉴를 파는 식당 + 해당 메뉴만
            results = Restaurant.objects.filter(menus__in=menu_match).distinct().prefetch_related(
                Prefetch('menus', queryset=menu_match, to_attr='filtered_menus')
            )
            serializer = RestaurantSerializer(
                results, many=True,
                context={'request': request, 'search_text': search_text}
            )
            return Response({
                "search_text": search_text,
                "type": "menu",
                "results": serializer.data
            })

        else:
            # 검색 결과 없음
            return Response({
                "search_text": search_text,
                "results": []
            })

class VoiceSearchView(APIView):
    def post(self, request):
        audio_file = request.FILES.get("audio")
        if not audio_file:
            return Response({"error":"오디오 파일 없음"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file
            )
            search_text = transcript.text.strip()
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        results = Restaurant.objects.filter(
            Q(name__icontains=search_text) |
            Q(address__icontains=search_text) |
            Q(tag__icontains=search_text) |
            Q(menus__name__icontains=search_text)
        ).distinct()

        serializer = RestaurantSerializer(results, many=True)
        return Response({
            "search_text": search_text,
            "results": serializer.data
        })