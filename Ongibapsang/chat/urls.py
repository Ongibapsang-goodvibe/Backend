from django.urls import path
from .views import ProcessAudioAPIView, EndChatAPIView

urlpatterns = [
    path('process-audio/', ProcessAudioAPIView.as_view(), name='process-audio'),
    path('end-chat/', EndChatAPIView.as_view(), name='end-chat'),
]
