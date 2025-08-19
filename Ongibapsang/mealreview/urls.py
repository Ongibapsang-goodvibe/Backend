from django.urls import path
from .views import DetailOptionView, MealLogView  # ← API 뷰 (DRF)

app_name = "mealreview"

urlpatterns = [
    path("options/",  DetailOptionView.as_view(),  name="api-options"),
    path("logs/", MealLogView.as_view(), name="api-logs"),
]
