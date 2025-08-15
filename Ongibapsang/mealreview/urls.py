from django.urls import path
from .views import ReviewOptionView, DetailOptionView, MealLogView  # ← API 뷰 (DRF)
from .views_pages import OverallPage, SelectPage, VoicePage, ConfirmPage   # ← UI 페이지 뷰

app_name = "mealreview"

urlpatterns = [
    # ===== UI (HTML 렌더) =====
    path("ui/overall/", OverallPage.as_view(), name="ui-overall"),
    path("ui/select/",  SelectPage.as_view(),  name="ui-select"),
    path("ui/voice/",   VoicePage.as_view(),   name="ui-voice"),
    path("ui/confirm/", ConfirmPage.as_view(), name="ui-confirm"),

    # ===== API (JSON) =====
    path("options/initial/", ReviewOptionView.as_view(), name="api-options-initial"),  # 쓰면 유지, 아니면 제거
    path("options/detail/",  DetailOptionView.as_view(),  name="api-options-detail"),
    path("logs/",            MealLogView.as_view(), name="api-logs"),
]
