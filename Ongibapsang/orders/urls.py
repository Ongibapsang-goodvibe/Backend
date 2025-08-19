from django.urls import path
from .views import OrderListView

app_name = "orders"
urlpatterns = [
    path("logs/", OrderListView.as_view(), name="orderList"),
]