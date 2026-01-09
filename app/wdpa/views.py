from django.http import JsonResponse
from django.core.cache import cache

from .services import search_wdpa

import logging

logger = logging.getLogger(__name__)


def search_place(request):
    name = request.GET.get("name", "")
    if not name:
        return JsonResponse({"error": "Missing 'name' parameter"}, status=400)

    cache_key = f"wdpa_{name}"
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse({"results": cached})

    try:
        results = search_wdpa(name)
    except RuntimeError as exc:
        logger.exception("WDPA search failed for name %r", name)
        return JsonResponse({"error": "Failed to fetch WDPA data"}, status=502)

    cache.set(cache_key, results, timeout=86400)
    return JsonResponse({"results": results})
