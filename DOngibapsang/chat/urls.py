from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('process_audio/', process_audio, name='process_audio'),
    path('end_chat/', end_chat, name='end_chat'),
]
