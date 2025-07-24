import logging
from typing import List, Dict

import requests

BASE_TGN_URL = "https://vocab.getty.edu/sparql.json"


LOG = logging.getLogger(__name__)


def search_tgn(name: str, place_type: str = None) -> List[Dict[str, str]]:
    """Query Getty TGN via SPARQL by place name and optional place type."""
    query = f"""
    SELECT ?place ?placeLabel ?coords ?placetypeLabel ?countryLabel ?continentLabel
    WHERE {{
      ?place rdfs:label ?placeLabel .
      FILTER(CONTAINS(LCASE(?placeLabel), LCASE(\"{name}\"))) .
      OPTIONAL {{ ?place gvp:placeTypePreferred ?placetype . ?placetype rdfs:label ?placetypeLabel. }}
      OPTIONAL {{ ?place gvp:broaderPreferred* ?country . ?country gvp:placeTypePreferred gvp:country . ?country rdfs:label ?countryLabel. }}
      OPTIONAL {{ ?place gvp:broaderPreferred* ?continent . ?continent gvp:placeTypePreferred gvp:continent . ?continent rdfs:label ?continentLabel. }}
      OPTIONAL {{ ?place wgs:lat ?lat ; wgs:long ?lon . BIND(CONCAT(STR(?lat), ",", STR(?lon)) AS ?coords) }}
    }}
    LIMIT 20
    """

    if place_type:
        query = query.replace(
            "WHERE {",
            f"""
            WHERE {{
              ?place gvp:placeTypePreferred ?ptype .
              ?ptype rdfs:label ?ptypeLabel .
              FILTER(CONTAINS(LCASE(?ptypeLabel), LCASE(\"{place_type}\"))) .
            """,
        )

    try:
        response = requests.get(BASE_TGN_URL, params={"query": query}, timeout=10)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        LOG.warning("TGN request failed: %s", exc)
        raise RuntimeError("Failed to query Getty TGN") from exc

    results = []
    for b in data.get("results", {}).get("bindings", []):
        results.append({
            "uri": b.get("place", {}).get("value"),
            "name": b.get("placeLabel", {}).get("value"),
            "coordinates": b.get("coords", {}).get("value") if "coords" in b else None,
            "place_type": b.get("placetypeLabel", {}).get("value") if "placetypeLabel" in b else None,
            "country": b.get("countryLabel", {}).get("value") if "countryLabel" in b else None,
            "continent": b.get("continentLabel", {}).get("value") if "continentLabel" in b else None,
        })
    return results
