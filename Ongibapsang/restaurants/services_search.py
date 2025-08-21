<<<<<<< HEAD
# restaurants/services_search.py
from django.db.models import Count
from .models import Restaurant, Menu, Ingredient, SearchLog

def simple_three_way_search(*, keyword: str, limit: int = 10):
    kw = (keyword or "").strip()
    if not kw:
        SearchLog.objects.create(text="", keyword="", stage="none")
        return "none", Menu.objects.none()
=======
# restaurant/services_search.py
from typing import List, Dict
from django.db.models import Count
from voice.models import Transcription
from .models import Restaurant, Menu, Ingredient, SearchLog

#메뉴 queryset을 카드(dict) 리스트로 변환
def _build_cards(menus_qs, limit=10) -> List[Dict]:
    menus = menus_qs.select_related("restaurant").order_by("name").distinct()[:limit]
    cards = []
    for m in menus:
        r = m.restaurant
        img = m.image.url if getattr(m, "image", None) else None
        cards.append({
            "menu_id": m.id,
            "menu_name": m.name,
            "price": m.price,
            "restaurant_id": r.id,
            "restaurant_name": r.name,
            "delivery_fee": r.delivery_fee,
            "delivery_time":r.delivery_time,
            "image_url": img,
        })
    return cards

#검색 우선순위 
def simple_three_way_search(*, keyword: str, transcription: Transcription | None, limit=10) -> dict:
    kw = (keyword or "").strip()
    if not kw:
        SearchLog.objects.create(source_transcription=transcription, keyword=kw, stage="none")
        return {"stage": "none", "cards": []}
>>>>>>> origin/backup_0821

    # 1) 식당명
    rest_qs = Restaurant.objects.filter(name__icontains=kw)
    if rest_qs.exists():
<<<<<<< HEAD
        qs = (Menu.objects.filter(restaurant__in=rest_qs)
              .select_related("restaurant")
              .annotate(hit=Count("restaurant"))
              .order_by("-hit", "name"))[:limit]
        SearchLog.objects.create(text=kw, keyword=kw, stage="restaurant")
        return "restaurant", qs
=======
        menus_qs = Menu.objects.filter(restaurant__in=rest_qs).annotate(hit=Count("restaurant")).order_by("-hit","name")
        cards = _build_cards(menus_qs, limit)
        SearchLog.objects.create(source_transcription=transcription, keyword=kw, stage="restaurant")
        return {"stage": "restaurant", "cards": cards}
>>>>>>> origin/backup_0821

    # 2) 메뉴명
    menu_qs = Menu.objects.filter(name__icontains=kw)
    if menu_qs.exists():
<<<<<<< HEAD
        qs = (menu_qs.select_related("restaurant").order_by("name"))[:limit]
        SearchLog.objects.create(text=kw, keyword=kw, stage="menu")
        return "menu", qs
=======
        cards = _build_cards(menu_qs, limit)
        SearchLog.objects.create(source_transcription=transcription, keyword=kw, stage="menu")
        return {"stage": "menu", "cards": cards}
>>>>>>> origin/backup_0821

    # 3) 재료
    ing_qs = Ingredient.objects.filter(name__icontains=kw)
    if ing_qs.exists():
<<<<<<< HEAD
        qs = (Menu.objects.filter(ingredients__in=ing_qs)
              .select_related("restaurant").distinct().order_by("name"))[:limit]
        SearchLog.objects.create(text=kw, keyword=kw, stage="ingredient")
        return "ingredient", qs

    # 4) 폴백
    fallback_menus = Menu.objects.filter(name__icontains=kw)
    if fallback_menus.exists():
        qs = fallback_menus.select_related("restaurant").order_by("name")[:limit]
    else:
        fallback_rests = Restaurant.objects.filter(name__icontains=kw)
        qs = (Menu.objects.filter(restaurant__in=fallback_rests)
              .select_related("restaurant").order_by("name"))[:limit]

    SearchLog.objects.create(text=kw, keyword=kw, stage="fallback")
    return "fallback", qs
=======
        menus_qs = Menu.objects.filter(ingredients__in=ing_qs).distinct()
        cards = _build_cards(menus_qs, limit)
        SearchLog.objects.create(source_transcription=transcription, keyword=kw, stage="ingredient")
        return {"stage": "ingredient", "cards": cards}

    # 4) 폴백
    fallback_menus = Menu.objects.filter(name__icontains=kw)
    fallback_rests = Restaurant.objects.filter(name__icontains=kw)
    menus_qs = fallback_menus if fallback_menus.exists() else Menu.objects.filter(restaurant__in=fallback_rests)
    cards = _build_cards(menus_qs, limit)
    SearchLog.objects.create(source_transcription=transcription, keyword=kw, stage="fallback")
    return {"stage": "fallback", "cards": cards}
>>>>>>> origin/backup_0821
