from django.urls import path
from .views import *


app_name = "voice"

urlpatterns = [
    path('transcribe/', TranscribeView.as_view(), name='transcribe'),
]