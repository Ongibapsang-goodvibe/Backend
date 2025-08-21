from django.shortcuts import render
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework import generics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import os
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from accounts.models import User
from orders.models import Order
from restaurants.recommendation import _kcal_of, _to_grams
from .models import *
from .serializers import *

# OpenAI: v1(new) 우선, 실패시 v0(old) fallback
try:
    from openai import OpenAI
    _OPENAI_CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    _OPENAI_IS_V1 = True
except Exception:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    _OPENAI_CLIENT = openai
    _OPENAI_IS_V1 = False

#해당 주의 월요일 00:00
def monday_set(dt: datetime):
    dt = timezone.now()
    start = dt - timedelta(days=dt.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    return timezone.make_aware(start.replace(tzinfo=None)) if timezone.is_naive(start) else start

#이번 주 월요일 00:00 ~ 현재 시각
def monday_to_now():
    now = timezone.now()
    start = monday_set(now)
    return start, now

#지난 주 월요일 00:00 ~ 이번 주 월요일 00:00
def lastweek():
    now = timezone.now()
    this_monday = now - timezone.timedelta(days=now.weekday())
    last_monday = this_monday - timezone.timedelta(days=7)
    return last_monday, this_monday

def weekly_data(user: User, disease_id: int, start, end):
    orders = (
        Order.objects.filter(user=user, time__gte=start, time__lt=end)
        .select_related("menu")
        .prefetch_related("menu__menu_nutritions__nutrient")
    )

    total_g = defaultdict(float)
    total_kcal = 0.0
    order_count = 0

    for o in orders:
        qty = int(o.quantity or 0)
        if qty <= 0:
            continue
        order_count += qty
        order_grams = dict(o.record_fixed or {})
        order_kcal = float(order_grams.pop("ENERGY", 0.0))

        total_kcal += order_kcal*qty
        for code, g in order_grams.items():
            try:
                total_g[code] += float(g) * qty
            except (ValueError, TypeError):
                continue
    
    carb_percent = _kcal_of("CARB",total_g.get("CARB", 0.0))
    prot_percent = _kcal_of("PROTEIN",total_g.get("PROTEIN", 0.0))
    fat_percent = _kcal_of("FAT",total_g.get("FAT", 0.0))
    s = carb_percent + prot_percent + fat_percent
    nutrient_percent = {
        "CARB": round(carb_percent / s * 100, 1) if s else 0.0,
        "PROTEIN": round(prot_percent / s * 100, 1) if s else 0.0,
        "FAT": round(fat_percent / s * 100, 1) if s else 0.0,
    }

    rules = DiseaseRules.objects.filter(disease_id=disease_id).select_related("nutrient")
    weekly_recommend = {}
    for r in rules:
        code = r.nutrient.code
        rec = {}
        # 1회 제공량 기준 → 주간 섭취 기준 (주문 수량 합 * mg → g)
        if r.min_once is not None:
            g = _to_grams(r.min_once, r.nutrient.unit)
            rec["weekly_min_g"] =  g * order_count
        if r.max_once is not None:
            g = _to_grams(r.max_once, r.nutrient.unit)
            rec["weekly_max_g"] = g * order_count

        # 열량 비율 기준 (메뉴 1회 기준의 % 기준을 '참고치'로 그대로 제공)
        if r.percent_min is not None:
            rec["percent_min"] = float(r.percent_min)
        if r.percent_max is not None:
            rec["percent_max"] = float(r.percent_max)

        # per_1000kcal (mg/1000kcal → g/1000kcal)
        if r.use_per_1000kcal:
            rec["per_1000kcal_min_g"] = (float(r.per_1000kcal_min) / 1000.0) if r.per_1000kcal_min is not None else None
            rec["per_1000kcal_max_g"] = (float(r.per_1000kcal_max) / 1000.0) if r.per_1000kcal_max is not None else None

        weekly_recommend[code] = rec

    return {
        "total_g": dict(total_g),
        "total_kcal": float(total_kcal),
        "nutrient_percent": nutrient_percent,
        "weekly_recommend": weekly_recommend,
        "order_count": order_count,
        "period_start": start,
        "period_end": end,
    }

def ai_api_calling(analysis: dict, disease_name: str):
    sys_prompt = "당신은 지금부터 영양사입니다. 간단하지만 정확한 주간 영양보고서를 작성해주세요."
    user_prompt = (
        "아래는 사용자의 최근 주간 식사 주문 기록과 질환별 권고치입니다. "
        "데이터를 분석해, 해당 질환 관점에서 주간 섭취 평가와 구체적 행동 팁을 한국어로 각각 한 문장씩 제공하세요. \n\n"
        f"- 질환: {disease_name}\n"
        f"- 분석데이터(JSON): {analysis}\n"
        "형식:\n"
        "1) 요약(한 문장)\n"
        "2) 비율/기준 대비 평가(불충분/과다 중심)\n"
        "3) 다음 주 행동 팁(글머리표)\n"
    )

    try:
        if _OPENAI_IS_V1:
            resp = _OPENAI_CLIENT.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
            )
            return resp.choices[0].message.content.strip()
        else:
            resp = _OPENAI_CLIENT.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
            )
            return resp.choices[0].message["content"].strip()
    except Exception as e:
        return f"AI 분석 실패: {e}"

class CurrentWeekNutritionReport(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        start, end = monday_to_now()
        all_diseases = user.diseases.all()
        combined_analysis = {}
        for disease in all_diseases:
            analysis = weekly_data(request.user, disease.id, start, end)
            ai_feedback = ai_api_calling(
                {
                    "total_g": analysis["total_g"],
                    "total_kcal": analysis["total_kcal"],
                    "nutrient_percent": analysis["nutrient_percent"],
                    "weekly_recommend": analysis["weekly_recommend"],
                    "order_count": analysis["order_count"],
                    "period": {
                        "start": str(analysis["period_start"]),
                        "end": str(analysis["period_end"]),
                    },
                },
                disease_name=disease.name,
            )
            combined_analysis[disease.name] = {
                "analysis": analysis,
                "ai_feedback": ai_feedback,
            }
        return Response(combined_analysis, status=status.HTTP_200_OK)

class LastWeekNutritionReport(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        last_monday, this_monday = lastweek()
        all_diseases = user.diseases.all()
        combined_analysis = {}
        for disease in all_diseases:
            analysis = weekly_data(request.user, disease.id, last_monday, this_monday)
            ai_feedback = ai_api_calling(
                {
                    "total_g": analysis["total_g"],
                    "total_kcal": analysis["total_kcal"],
                    "nutrient_percent": analysis["nutrient_percent"],
                    "weekly_recommend": analysis["weekly_recommend"],
                    "order_count": analysis["order_count"],
                    "period": {
                        "start": str(analysis["period_start"]),
                        "end": str(analysis["period_end"]),
                    },
                },
                disease_name=disease.name,
            )
            combined_analysis[disease.name] = {
                "analysis": analysis,
                "ai_feedback": ai_feedback,
            }
        return Response(combined_analysis, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        last_monday, this_monday = lastweek()
        all_diseases = user.diseases.all()
        result = {}
        for disease in all_diseases:
            analysis = weekly_data(request.user, disease.id, last_monday, this_monday)
            ai_feedback = ai_api_calling(
                {
                    "total_g": analysis["total_g"],
                    "total_kcal": analysis["total_kcal"],
                    "nutrient_percent": analysis["nutrient_percent"],
                    "weekly_recommend": analysis["weekly_recommend"],
                    "order_count": analysis["order_count"],
                    "period": {
                        "start": str(analysis["period_start"]),
                        "end": str(analysis["period_end"]),
                    },
                },
                disease_name=disease.name,
            )

            report, created = NutritionReport.objects.get_or_create(
                user=user,
                disease=disease,
                date=last_monday.date(),  # 지난주 월요일
            )

            # 확정 저장
            report.total_nutrients = dict(analysis["total_g"])
            report.macro_percent = analysis["nutrient_percent"]
            report.weekly_recommendation = analysis["weekly_recommendation"]
            report.note = ai_feedback
            report.save()

            result[disease.name] = {
                "analysis": analysis,
                "ai_feedback": ai_feedback,
                "finalized": True,
                "report_id": report.id,
                "created_new_report": created,
            }

        return Response(result, status=status.HTTP_200_OK)
    
#---------------------------------------------------------------------------------------------------
#DB 저장용
class HealthcareLogView(generics.CreateAPIView):
    serializer_class=HealthcareLogSerializer
    permission_classes=[AllowAny]
    parser_classes=[JSONParser, FormParser, MultiPartParser] #JSON/폼 다 받기

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

class HealthReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        '''
        last_monday, this_monday = lastweek()

        logs = HealthcareLog.objects.filter(
            user=user,
            created_at__gte=last_monday,
            created_at__lt=this_monday
        )
        '''
        start, now = monday_to_now()

        logs = HealthcareLog.objects.filter(
            #user=user,
            created_at__gte=start, #last_monday,
            created_at__lt=now #this_monday
        )
        # BAD 개수 & BAD 로그
        bad_logs = logs.filter(initial_label="BAD")
        bad_count = bad_logs.count()
        bad_logs_serializer = HealthcareLogSerializer(bad_logs, many=True).data

        # mood 집계
        mood_list = [log.mood_label for log in logs if log.mood_label]
        mood_counts = dict(Counter(mood_list))
        dominant_mood = max(mood_counts.items(), key=lambda x: x[1])[0] if mood_counts else None

        # 요일별 BAD 텍스트 + 요일별 mood count
        weekday_bad_texts = defaultdict(list)
        weekday_moods = defaultdict(list)

        for log in logs:
            KOREAN_WEEKDAYS = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
            weekday = KOREAN_WEEKDAYS[log.created_at.weekday()]
            if log.initial_label == HealthcareOption.BAD:
                weekday_bad_texts[weekday].append(log.text)
            if log.mood_label:
                weekday_moods[weekday].append(log.mood_label)
        
        #요일별 mood 카운트로 변환
        weekday_mood_counts = {
            day: dict(Counter(moods)) for day, moods in weekday_moods.items()
        }
        
        payload = {
            "period_start": start, #last_monday,
            "period_end": now - timezone.timedelta(days=1), #this_monday
            "bad_count": bad_count,
            "bad_logs": bad_logs_serializer,
            "dominant_mood": dominant_mood,
            "mood_counts": mood_counts,
            "weekday_bad_texts": dict(weekday_bad_texts),
            "weekday_mood_counts": weekday_mood_counts,
        }

        serializer = H_AnalysisSerializer(payload)
        return Response(serializer.data)
    
        