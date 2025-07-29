import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

logger = logging.getLogger(__name__)


def search_tgn(name):
    logger.debug(f"Starting TGN search for name: {name}")

    base_url = "https://www.getty.edu/vow/TGNServlet"
    search_params = {
        "find": name,
        "place": "",
        "nation": "",
        "english": "Y",
        "page": "1",
    }

    try:
        search_response = requests.get(base_url, params=search_params, timeout=10)
        logger.debug(f"Constructed search URL: {search_response.url}")
        logger.debug(f"Search page HTML (first 500 chars): {search_response.text[:500]}")
        search_response.raise_for_status()
    except requests.RequestException as e:
        logger.warning(f"TGN search request failed: {e}")
        return []

    soup = BeautifulSoup(search_response.text, 'html.parser')
    links = soup.select("a[href*='TGNFullDisplay?']")
    logger.debug(f"Found {len(links)} TGN display links.")

    results = []

    for link in links:
        href = link.get("href")
        full_url = urljoin("https://www.getty.edu/vow/", href)
        logger.debug(f"Fetching display page: {full_url}")

        try:
            detail_response = requests.get(full_url, timeout=10)
            detail_response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {full_url}: {e}")
            continue

        detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

        tgn_id = href.split("subjectid=")[-1] if "subjectid=" in href else "NA"

        # Preferred name extraction
        preferred_name_tag = detail_soup.find("a", onmouseover=lambda x: x and "Preferred Name" in x)
        preferred_name = "NA"
        if preferred_name_tag:
            bold_parent = preferred_name_tag.find_parent("nobr")
            if bold_parent:
                bold_text = bold_parent.find("b")
                if bold_text:
                    preferred_name = bold_text.get_text(strip=True)

        # Place type extraction
        place_type = "NA"
        for td in detail_soup.select("td[colspan='4'][valign='BOTTOM'] span.page b"):
            text = td.get_text(strip=True)
            if '(' in text and ')' in text:
                place_type = text.split('(')[-1].rstrip(')')
                break

        # Coordinates (decimal degrees)
        latitude = "NA"
        longitude = "NA"
        for span in detail_soup.find_all("span", class_="page"):
            full_text = span.get_text(separator=" ", strip=True).replace("\xa0", " ")
            logger.debug(f"Coordinate candidate text: {full_text}")
            if "Lat:" in full_text and "decimal degrees" in full_text:
                try:
                    latitude = full_text.split("Lat:")[1].split("decimal degrees")[0].strip()
                except Exception as e:
                    logger.warning(f"Error parsing latitude: {e}")
            if "Long:" in full_text and "decimal degrees" in full_text:
                try:
                    longitude = full_text.split("Long:")[1].split("decimal degrees")[0].strip()
                except Exception as e:
                    logger.warning(f"Error parsing longitude: {e}")

        # Hierarchy extraction
        hierarchy = {
            "Continent": "",
            "Country": "",
            "State or Province": "NA",
            "County": "NA",
            "Municipality": "NA"
        }
        table_tags = detail_soup.select("td span.page")
        for tag in table_tags:
            txt = tag.get_text()
            if "(continent)" in txt:
                hierarchy["Continent"] = txt.split("(")[0].strip()
            elif "(nation)" in txt:
                hierarchy["Country"] = txt.split("(")[0].strip()
            elif "(state)" in txt:
                hierarchy["State or Province"] = txt.split("(")[0].strip()
            elif "(province)" in txt:
                hierarchy["State or Province"] = txt.split("(")[0].strip()
            elif "(county)" in txt:
                hierarchy["County"] = txt.split("(")[0].strip()
            elif "(municipality)" in txt:
                hierarchy["Municipality"] = txt.split("(")[0].strip()

        result = {
            "tgn_id": tgn_id,
            "preferred_name": preferred_name,
            "place_type": place_type,
            "latitude": latitude,
            "longitude": longitude,
            **hierarchy
        }

        logger.debug(f"Parsed TGN display result: {result}")
        results.append(result)

    logger.info(f"TGN search completed: {len(results)} result(s) found for '{name}'")
    return results
