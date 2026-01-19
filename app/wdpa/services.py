import logging
import json
import html
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_WDPA_URL = "https://www.protectedplanet.net"
BASE_WDPA_SEARCH_URL = urljoin(BASE_WDPA_URL, "/en/search-areas")

logger = logging.getLogger(__name__)


def _find_attr_json(soup, attr_name):
    """Return parsed JSON from an attribute with name ``attr_name`` if present."""
    tag = next((t for t in soup.find_all(True) if t.has_attr(attr_name)), None)
    if not tag:
        return None
    try:
        return json.loads(html.unescape(tag[attr_name]))
    except Exception as exc:  # pragma: no cover - safety
        logger.warning(f"Failed to parse JSON for {attr_name}: {exc}")
        return None


def search_wdpa(name):
    """Search the WDPA for ``name`` and return parsed result dictionaries."""
    logger.debug(f"Starting WDPA search for name: {name}")
    params = {"search_term": name, "geo_type": "site"}
    try:
        resp = requests.get(BASE_WDPA_SEARCH_URL, params=params, timeout=10)
        logger.debug(f"Constructed search URL: {resp.url}")
        logger.debug(f"Search page HTML (first 500 chars): {resp.text[:500]}")
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning(f"WDPA search request failed: {exc}")
        raise RuntimeError(f"Failed to query Protected Planet: {exc}")

    soup = BeautifulSoup(resp.text, "html.parser")
    results_data = _find_attr_json(soup, ":results") or {}
    areas = results_data.get("areas", [])

    results = []
    for area in areas:
        url = area.get("url")
        if not url:
            continue
        wdpa_id = url.lstrip("/")
        detail_url = urljoin(BASE_WDPA_URL, url.lstrip("/"))
        try:
            d_resp = requests.get(detail_url, timeout=10)
            d_resp.raise_for_status()
        except requests.RequestException as exc:
            logger.warning(f"Failed to fetch {detail_url}: {exc}")
            continue
        detail_soup = BeautifulSoup(d_resp.text, "html.parser")
        country_tag = detail_soup.select_one('a[href^="/en/country/"]')
        country = country_tag.get_text(strip=True) if country_tag else "NA"
        attr_info = _find_attr_json(detail_soup, ":attributes-info")
        original_name = "NA"
        if attr_info:
            name_candidates = {}
            for item in attr_info[0].get("attributes", []):
                title = item.get("title")
                if title in {"Original Name", "Name", "English Name"}:
                    name_candidates[title] = item.get("value", "NA")
            for title in ("Original Name", "Name", "English Name"):
                if name_candidates.get(title):
                    original_name = name_candidates[title]
                    break
        results.append({
            "wdpa_id": wdpa_id,
            "original_name": original_name,
            "country": country,
        })

    logger.info(f"WDPA search completed: {len(results)} result(s) found for '{name}'")
    return results
