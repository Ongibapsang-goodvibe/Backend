from django.urls import path, include
from .views import DetailOptionView, MealLogView, MenuReviewSummary

app_name = "mealreview"

urlpatterns = [
    path("options/",  DetailOptionView.as_view(),  name="api-options"),
    path("logs/", MealLogView.as_view(), name="api-logs"),
    path("menus/<int:menu_id>/reviews/",MenuReviewSummary.as_view(), name="api-meallog" )
]
