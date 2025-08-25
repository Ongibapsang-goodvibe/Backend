from django.urls import path
from healthcare.views import *

app_name = "healthcare"

urlpatterns = [
    path("logs/", HealthcareLogView.as_view(), name="api-healthcare-logs"),
    # 이번 주 보고서 조회 (이번주 월요일부터 현재까지)
    path("n_report/currentweek/", CurrentWeekNutritionReport.as_view(), name="current_week_nutrition_report"),
    # 지난 주 보고서 확정 (지난주 월요일부터 일요일까지)
    path("n_report/lastweek/", LastWeekNutritionReport.as_view(), name="last_week_nutrition_report"),
    path("h_report/", HealthReportView.as_view(), name="health_report"),
    path("reports/send/", SendWeeklyReportView.as_view(), name="healthcare-send-report")
]


