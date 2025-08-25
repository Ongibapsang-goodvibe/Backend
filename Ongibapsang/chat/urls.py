from django.urls import path
from .views import ProcessAudioAPIView, EndChatAPIView, serve_audio

urlpatterns = [
    path('process-audio/', ProcessAudioAPIView.as_view(), name='process-audio'),
    path('end-chat/', EndChatAPIView.as_view(), name='end-chat'),
    path('media/<str:filename>', serve_audio, name='serve-audio'),
]
