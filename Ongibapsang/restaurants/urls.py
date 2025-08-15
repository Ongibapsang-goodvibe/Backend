# restaurant/urls.py
from django.urls import path
from django.views.generic import TemplateView
from .views import SearchByTranscriptionView
from .views_pages import OrderResultsPage, VoiceSearchPage

app_name = "restaurants"

urlpatterns = [
    # 1) 선택 페이지 (음성 vs. 타자)
    path("search/", TemplateView.as_view(template_name="search_landing.html"), name="search-landing"),

    # 2) 텍스트 검색 입력 페이지 (기존 페이지 사용)
    path("search/text/", TemplateView.as_view(template_name="order_voice.html"), name="search-text"),

    # 3) 음성 인식 페이지 (여기서 브라우저 음성→텍스트)
    path("search/voice/", VoiceSearchPage.as_view(), name="search-voice"),

    # 4) 결과 페이지(서버 렌더, GET)
    path("results/", OrderResultsPage.as_view(), name="order-results"),

    # 5) 검색 API (JSON, POST)  ← 페이지가 아니라 API!
    path("api/search", SearchByTranscriptionView.as_view(), name="search-api"),
]

