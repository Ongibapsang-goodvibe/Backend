# restaurant/urls.py
from django.urls import path
from .views import SearchView

app_name = "restaurants"

urlpatterns = [
    # 검색 api 
    path("search/", SearchView.as_view(), name="search-api"),
]

