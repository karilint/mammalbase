from django.http import JsonResponse
from django.core.cache import cache

from .services import search_tgn


def search_place(request):
    name = request.GET.get("name", "")
    place_type = request.GET.get("place_type", "")

    if not name:
        return JsonResponse({"error": "Missing 'name' parameter"}, status=400)

    cache_key = f"tgn_{name}_{place_type}"
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse({"results": cached})

    try:
#        results = search_tgn(name, place_type if place_type else None)
        results = search_tgn(name)
    except RuntimeError as exc:
        return JsonResponse({"error": str(exc)}, status=502)

    cache.set(cache_key, results, timeout=86400)
    return JsonResponse({"results": results})
