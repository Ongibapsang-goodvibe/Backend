from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework import generics
from .models import *
from .serializers import * 
from django.db.models import Q, Count

# Create your views here.
class DetailOptionView(generics.ListAPIView):
    serializer_class = DetailOptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        init = self.request.query_params.get("kind")
        qs = DetailOption.objects.order_by("kind", "sort_order", "id")
        return qs.filter(kind=init) if init else qs.none()

# DB 저장용 
class MealLogView(generics.CreateAPIView):
    serializer_class = MealLogSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser] 

    #리뷰 작성자 유저 정보 저장 
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

def _mask(name: str) -> str:
    name = (name or "").strip() or "익명"
    return f"{name[:1]}**"


class MenuReviewSummary(generics.ListCreateAPIView):
    """
    GET  /api/restaurants/menus/<menu_id>/reviews/
        -> {
             "summary": { "GOOD": [...], "BAD": [...] },  # 버튼 옵션 집계 (sort_order 순)
             "reviews": [ {id, text, created_at, author}, ... ]  # 텍스트 후기(최신순)
           }

    POST /api/restaurants/menus/<menu_id>/reviews/
        - 기존 MealLog 생성과 동일(Serializer 유지)
    """
    serializer_class = MealLogSerializer
    permission_classes = [IsAuthenticated]

    # path 파라미터(menu_id) 우선 사용, 없으면 쿼리스트링(menu) 허용
    def _get_menu_id(self):
        return self.kwargs.get("menu_id") or self.request.query_params.get("menu")

    # 하단 “직접 남긴 후기” 리스트용 쿼리셋 (텍스트 있는 것만)
    def get_queryset(self):
        qs = MealLog.objects.all()

        menu_id = self._get_menu_id()
        if menu_id:
            qs = qs.filter(order__menu_id=menu_id)

        # 텍스트 없는 로그는 제외
        qs = qs.exclude(text__isnull=True).exclude(text__exact="")

        return qs.select_related("order", "user").order_by("-created_at")

    # 상단 요약(옵션별 카운트) + 하단 텍스트 후기 리스트를 함께 반환
    def list(self, request, *args, **kwargs):
        # ----- (A) 텍스트 후기 -----
        qs = self.get_queryset()
        objs = list(qs)
        ser = self.get_serializer(objs, many=True)

        reviews = []
        for obj, row in zip(objs, ser.data):
            username = getattr(obj.user, "username", "") or getattr(obj.user, "first_name", "")
            reviews.append({
                "id": row["id"],
                "text": row["text"],
                "created_at": row["created_at"],
                "author": _mask(username),
            })

        # ----- (B) 옵션별 카운트 요약 -----
        menu_id = self._get_menu_id()

        # 버튼 입력만 집계 + 옵션 지정된 로그만
        log_filter = Q(source=Source.BUTTON) & Q(option__isnull=False)
        if menu_id:
            log_filter &= Q(order__menu_id=menu_id)

        # option_id 별 선택 횟수
        counts = (
            MealLog.objects
            .filter(log_filter)
            .values("option_id")
            .annotate(cnt=Count("id"))
        )
        counts_map = {r["option_id"]: r["cnt"] for r in counts}

        # 활성 옵션 전부를 kind(GOOD/BAD) → sort_order → id 순으로 내려줌
        options = (
            DetailOption.objects
            .filter(is_active=True)
            .order_by("kind", "sort_order", "id")
            .values("id", "kind", "label", "sort_order")
        )

        summary = {"GOOD": [], "BAD": []}  # 기본 키 구성
        for o in options:
            group = o["kind"] or "GOOD"  # 혹시 None이면 GOOD로
            if group not in summary:
                summary[group] = []
            summary[group].append({
                "label": o["label"],
                "sort_order": o["sort_order"],
                "count": counts_map.get(o["id"], 0),
            })

        return Response({
            "summary": summary,
            "reviews": reviews,
        })

    # 생성 로직은 그대로(작성자 자동 세팅)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
