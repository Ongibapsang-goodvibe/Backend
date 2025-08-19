from django.urls import path
from .views import OrderListView, RecommendAPIView

app_name = "orders"
urlpatterns = [
    path("", OrderListView.as_view(), name="orderList"),
    path("recommend/", RecommendAPIView.as_view(), name="recommend"),
]