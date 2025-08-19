# restaurants/services_search.py
from django.db.models import Count
from .models import Restaurant, Menu, Ingredient, SearchLog

def simple_three_way_search(*, keyword: str, limit: int = 10):
    kw = (keyword or "").strip()
    if not kw:
        SearchLog.objects.create(text="", keyword="", stage="none")
        return "none", Menu.objects.none()

    # 1) 식당명
    rest_qs = Restaurant.objects.filter(name__icontains=kw)
    if rest_qs.exists():
        qs = (Menu.objects.filter(restaurant__in=rest_qs)
              .select_related("restaurant")
              .annotate(hit=Count("restaurant"))
              .order_by("-hit", "name"))[:limit]
        SearchLog.objects.create(text=kw, keyword=kw, stage="restaurant")
        return "restaurant", qs

    # 2) 메뉴명
    menu_qs = Menu.objects.filter(name__icontains=kw)
    if menu_qs.exists():
        qs = (menu_qs.select_related("restaurant").order_by("name"))[:limit]
        SearchLog.objects.create(text=kw, keyword=kw, stage="menu")
        return "menu", qs

    # 3) 재료
    ing_qs = Ingredient.objects.filter(name__icontains=kw)
    if ing_qs.exists():
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
