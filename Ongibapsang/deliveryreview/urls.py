from django.urls import path
from .views import DetailOptionView, DeliveryLogView

app_name = "deliveryreview"

urlpatterns = [
    path("options/", DetailOptionView.as_view(), name="api-options"),
    path("logs/", DeliveryLogView.as_view(), name="api-logs"), 
]