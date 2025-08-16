import json
from django.core.management.base import BaseCommand, CommandError
from restaurants.services_search import simple_three_way_search
from restaurants.serializers import MenuCardSerializer

class Command(BaseCommand):
    help = "Search restaurants/menus/ingredients by text and print MenuCardSerializer JSON."

    def add_arguments(self, parser):
        parser.add_argument("text", type=str, help="검색 키워드 (예: '두부', '맛나식당', '순두부찌개')")
        parser.add_argument("--limit", type=int, default=10)

    def handle(self, *args, **opts):
        kw = (opts["text"] or "").strip()
        if not kw:
            raise CommandError("text is required")
        result = simple_three_way_search(keyword=kw, transcription=None, limit=opts["limit"])
        payload = {
            "stage": result["stage"],
            "cards": MenuCardSerializer(result["cards"], many=True).data,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))