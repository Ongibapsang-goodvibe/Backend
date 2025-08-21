# restaurant/urls.py
from django.urls import path
from .views import SearchView, CategoryView, RecommendMenuView

app_name = "restaurants"

urlpatterns = [
    path("search/", SearchView.as_view(), name="search-api"), # 검색 api 
    path("menus/", CategoryView.as_view(), name="menu-category-api"), #카테고리별 분류 api 
    path('recommend/', RecommendMenuView.as_view(), name='recommend_menu'),
]   

