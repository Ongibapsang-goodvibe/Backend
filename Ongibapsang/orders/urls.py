from django.urls import path
from .views import *

app_name = "orders"
urlpatterns = [
    path("make/", MakeOrderView.as_view(), name="makeorders"),
    path("delete/<int:id>", DeleteOrderView.as_view(), name="deleteorder"),
    path("list/", OrderListView.as_view(), name="listorders"),
    path("detail/<int:id>", OrderDetailView.as_view(), name="detailorder"),
    path("recommend/", RecommendAPIView.as_view(), name="recommend"),
    path("orderoutput/", OrderOutputView.as_view(), name="order-output")
]