from django.urls import path
from .views import HealthcareLogView

app_name = "healthcare"

urlpatterns = [
    path("logs/", HealthcareLogView.as_view(), name="api-healthcare-logs")
]


