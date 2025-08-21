# restaurants/recommendation.py
from collections import defaultdict
from datetime import timedelta

from django.utils import timezone
from django.db.models import Prefetch

from accounts.models import User
from orders.models import Order
from restaurants.models import Menu, MenuNutrition, Nutrient
from healthcare.models import DiseaseRules

# -----------------------------
# 단위 변환 & 에너지 계산
# -----------------------------

def _to_grams(value: float, unit: str | None) -> float:
    """질량/부피 단위를 g로 통일"""
    if value is None:
        return 0.0
    if not unit:
        return float(value)
    u = unit.lower()
    if u == "g":
        return float(value)
    if u == "mg":
        return float(value) / 1000.0
    if u in ("µg", "μg", "ug"):
        return float(value) / 1_000_000.0
    if u == "ml":
        return float(value)
    if u == "kcal":
        return float(value)
    return float(value)

KCAL_PER_G = {
    "CARB": 4.0,
    "PROTEIN": 4.0,
    "FAT": 9.0,
    "SUGAR": 4.0,
    "SAT_FAT": 9.0,
}

def _energy_from_macros_g(nutr_g: dict) -> float:
    """CARB/PROTEIN/FAT g → kcal"""
    carb = nutr_g.get("CARB", 0.0)
    protein = nutr_g.get("PROTEIN", 0.0)
    fat = nutr_g.get("FAT", 0.0)
    return carb * 4.0 + protein * 4.0 + fat * 9.0

def _kcal_of(code: str, grams: float) -> float:
    f = KCAL_PER_G.get(code, 0.0)
    return grams * f

# -----------------------------
# 메뉴 영양소 계산
# -----------------------------

def _menu_nutrients_g_and_energy(menu: Menu) -> tuple[dict, float]:
    grams = defaultdict(float)
    kcal_direct = None

    for mn in menu.menu_nutritions.all():
        code = mn.nutrient.code  # pk 기반이면 id도 가능
        unit = mn.nutrient.unit or ""
        val = float(mn.amount)
        if unit.lower() == "kcal" or code == "ENERGY":
            kcal_direct = (kcal_direct or 0.0) + val
            continue
        grams[code] += _to_grams(val, unit)

    total_kcal = kcal_direct if kcal_direct is not None else _energy_from_macros_g(grams)
    return dict(grams), float(total_kcal)

# -----------------------------
# 질환 규칙 적용
# -----------------------------

def _collect_rules(user: User) -> dict:
    """질환별 DiseaseRules 병합 (엄격 적용)"""
    rules_qs = DiseaseRules.objects.filter(disease__in=user.diseases.all()).select_related("nutrient")
    merged = {}

    for r in rules_qs:
        code = r.nutrient.code  # id 기반 가능
        cur = merged.setdefault(code, {
            "abs_min_once_g": None,
            "abs_max_once_g": None,
            "percent_min": None,
            "percent_max": None,
            "per_1000kcal": r.use_per_1000kcal,
            "per_1000kcal_min_g": None,
            "per_1000kcal_max_g": None,
        })

        if r.min_once is not None:
            g = float(r.min_once) / 1000.0  # mg → g
            if r.use_per_1000kcal:
                cur["per_1000kcal_min_g"] = g if cur["per_1000kcal_min_g"] is None else max(cur["per_1000kcal_min_g"], g)
            else:
                cur["abs_min_once_g"] = g if cur["abs_min_once_g"] is None else max(cur["abs_min_once_g"], g)

        if r.max_once is not None:
            g = float(r.max_once) / 1000.0  # mg → g
            if r.use_per_1000kcal:
                cur["per_1000kcal_max_g"] = g if cur["per_1000kcal_max_g"] is None else min(cur["per_1000kcal_max_g"], g)
            else:
                cur["abs_max_once_g"] = g if cur["abs_max_once_g"] is None else min(cur["abs_max_once_g"], g)
        
        if r.percent_min is not None:
            p = float(r.percent_min)
            cur["percent_min"] = p if cur["percent_min"] is None else max(cur["percent_min"], p)
        if r.percent_max is not None:
            p = float(r.percent_max)
            cur["percent_max"] = p if cur["percent_max"] is None else min(cur["percent_max"], p)

    return merged

# -----------------------------
# 추천 메뉴 메인
# -----------------------------

def main_recommend(user: User, limit: int = 10) -> dict:
    rules = _collect_rules(user)
    since = timezone.now() - timedelta(days=7)

    orders = Order.objects.filter(user=user, time__gte=since).select_related("menu").prefetch_related(
        Prefetch("menu__menu_nutritions", queryset=MenuNutrition.objects.select_related("nutrient"))
    )

    totals_g = defaultdict(float)
    total_kcal = 0.0
    total_count = 0

    for o in orders:
        qty = int(o.quantity or 0)
        if qty <= 0:
            continue
        total_count += qty
        grams = o.record_fixed.copy()  # dict 복사
        kcal = grams.pop("ENERGY", 0.0)  # ENERGY는 kcal로 분리
        for c, g in grams.items():
    # 숫자형 값만 처리
            try:
                totals_g[c] += float(g) * qty
                total_kcal += float(kcal) * qty
            except (ValueError, TypeError):
                # 숫자가 아니면 무시
                continue
            
    menus = Menu.objects.prefetch_related(
        Prefetch("menu_nutritions", queryset=MenuNutrition.objects.select_related("nutrient"))
    ).select_related("restaurant").all()

    avoided = []
    candidates = []

    for m in menus:
        grams, kcal = _menu_nutrients_g_and_energy(m)
        violated = None

        #1차: 1회 제공량 기준    
        for code, rule in rules.items():
            once_max = rule.get("abs_max_once_g")
            if once_max is not None and grams.get(code, 0.0) > once_max:
                violated = f"{code}: exceeds abs_max_once_g {once_max}g"
                break
        if violated:
            avoided.append({"menu_id": m.id, "menu_name": m.name, "reason": violated})
            continue

        #2차: 1000kcal 당 mg 기준
        for code, rule in rules.items():
            if not rule.get("per_1000kcal"):
                continue
            kcal_factor = kcal / 1000.0 if kcal > 0 else 1.0
            g_per_1000kcal = grams.get(code, 0.0) / kcal_factor
            per_1000kcal_min = rule.get("per_1000kcal_min_g")
            per_1000kcal_max = rule.get("per_1000kcal_max_g")
            if per_1000kcal_min is not None and g_per_1000kcal < per_1000kcal_min:
                violated = f"{code}: per_1000kcal < {per_1000kcal_min:.3f}g"
                break
            if per_1000kcal_max is not None and g_per_1000kcal > per_1000kcal_max:
                violated = f"{code}: per_1000kcal > {per_1000kcal_max:.3f}g"
                break

        if violated:
            avoided.append({"menu_id": m.id, "menu_name": m.name, "reason": violated})
            continue

        candidates.append((m, grams, kcal))

        #3차: 총 열량 대비 탄단지 비율
        for code, rule in rules.items():
            if rule.get("per_1000kcal"):
                continue
            min_percent = rule.get("percent_min")
            max_percent = rule.get("percent_max")
            nutrient_kcal = _kcal_of(code, grams.get(code, 0.0))
            ratio = (nutrient_kcal / kcal * 100) if kcal > 0 else 0
            if min_percent is not None and ratio < min_percent:
                violated = f"{code}: percent<{min_percent:.1f}%"
                break
            if max_percent is not None and ratio > max_percent:
                violated = f"{code}: percent>{max_percent:.1f}%"
                break

        if violated:
            avoided.append({"menu_id": m.id, "menu_name": m.name, "reason": violated})
            continue


    # 부족분 점수 계산
    scored = []
    for m, grams, kcal in candidates:
        score = 0.0
        for code, rule in rules.items():
            if rule.get("per_1000kcal"):
                continue  # 1000kcal 기준만 적용, 부족분 계산 제외

            abs_min = rule.get("abs_min_once_g")
            if abs_min is not None:
                deficit = max(0.0, abs_min - totals_g.get(code, 0.0))
                score += min(deficit, grams.get(code, 0.0))
        scored.append((score, m, grams, kcal))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:limit]

    def _macro_energy_breakdown_percent(grams, kcal):
        if kcal <= 0:
            return {"CARB": 0.0, "PROTEIN": 0.0, "FAT": 0.0}
        carb_k = _kcal_of("CARB", grams.get("CARB", 0.0))
        prot_k = _kcal_of("PROTEIN", grams.get("PROTEIN", 0.0))
        fat_k = _kcal_of("FAT", grams.get("FAT", 0.0))
        s = carb_k + prot_k + fat_k
        if s <= 0:
            return {"CARB": 0.0, "PROTEIN": 0.0, "FAT": 0.0}
        return {
            "CARB": round(carb_k / s * 100, 1),
            "PROTEIN": round(prot_k / s * 100, 1),
            "FAT": round(fat_k / s * 100, 1),
        }

    def _menu_to_card(menu, grams, kcal):
        r = menu.restaurant
        return {
            "menu_id": menu.id,
            "menu_name": menu.name,
            "price": menu.price,
            "restaurant_id": r.id,
            "restaurant_name": r.name,
            "delivery_fee": r.delivery_fee,
            "image_url": menu.image.url if getattr(menu, "image", None) else None,
            "energy_kcal": round(kcal, 1),
            "macro_percent": _macro_energy_breakdown_percent(grams, kcal), #탄단지 퍼센트
        }

    return {
        "recommended": [
            _menu_to_card(m, grams, kcal) | {"score": round(score, 3)}
            for score, m, grams, kcal in top
        ],
        "avoided": avoided[:limit],
        "reason": {
            "orders_last_7d": total_count,
            "weekly_kcal": round(total_kcal, 1),
        }
    }
