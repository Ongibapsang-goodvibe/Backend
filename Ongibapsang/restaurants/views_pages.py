# restaurants/views_pages.py
from django.shortcuts import render
from django.views import View
from voice.models import Transcription
from .services_search import simple_three_way_search


# GET /results/?q=키워드   또는   /results/?tr=전사ID
class OrderResultsPage(View):
    """
    /results/?q=키워드  또는  /results/?tr=전사ID  로 들어오면
    서비스 함수를 호출해 카드 리스트를 서버에서 렌더링한다.
    """
    template_name = "order_result.html"

    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        tr_id = request.GET.get("tr")
        limit = int(request.GET.get("limit") or 10)

        tr = None
        keyword = q
        if not keyword and tr_id:
            tr = Transcription.objects.filter(pk=tr_id).first()
            keyword = (tr.text or "") if tr else ""

        result = simple_three_way_search(keyword=keyword, transcription=tr, limit=limit)

        context = {
            "keyword": keyword,
            "stage": result["stage"],
            "log": result.get("log"),
            "cards": result["cards"],   # dict 리스트 (menu_id, menu_name, price, restaurant_*, ...)
            "limit": limit,
        }
        return render(request, self.template_name, context)


# 음성 페이지 
class VoiceSearchPage(View):
    template_name = "voice_search.html"
    
    def get(self, request):
        return render(request, self.template_name)