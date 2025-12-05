from django.http import JsonResponse
from django.core.cache import cache

from .services import search_tgn


def search_place(request):
    name = request.GET.get("name", "")
    nature_reserve_param = request.GET.get("nature_reserve", "").lower()
    nature_reserve = nature_reserve_param in {"yes", "true", "1"}

    if not name:
        return JsonResponse({"error": "Missing 'name' parameter"}, status=400)

    cache_key = f"tgn_{name}_{nature_reserve}"
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse({"results": cached})

    try:
        results = search_tgn(name, nature_reserve)
    except RuntimeError as exc:
        return JsonResponse({"error": str(exc)}, status=502)

    cache.set(cache_key, results, timeout=86400)
    return JsonResponse({"results": results})
