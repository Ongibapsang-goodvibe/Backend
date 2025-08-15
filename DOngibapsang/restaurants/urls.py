from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

app_name = 'restaurants'

urlpatterns = [
    path('menu/', MenuListView.as_view(), name='menu-list'),
    path('restaurant/', RestaurantListView.as_view(), name='restaurant-list'),
    path('voice-search/', VoiceSearchView.as_view(), name='voice-search'),
    path('text-search/', TextSearchView.as_view(), name='text-search'),
]