import feedparser
import csv
import json
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from pytrends.request import TrendReq

logger = logging.getLogger(__name__)


def fetch_rss(urls: List[str]) -> List[Dict[str, str]]:
    """Récupère les entrées d’un ou plusieurs flux RSS."""
    items = []
    for url in urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                items.append({
                    "source": url,
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "snippet": entry.get("summary", ""),
                })
        except Exception as e:
            logger.warning(f"[veille] Erreur RSS {url} : {e}")
    return items


def fetch_google_trends(kw_list: List[str]) -> List[Dict[str, str]]:
    """Interroge Google Trends pour une liste de mots-clés."""
    pytrends = TrendReq(hl='fr-FR', tz=360)
    try:
        pytrends.build_payload(kw_list, timeframe='now 7-d')
        data = pytrends.interest_over_time()
    except Exception as e:
        logger.warning(f"[veille] Google Trends indisponible ({e}), skip.")
        return []

    items = []
    for kw in kw_list:
        series = data[kw].tolist() if kw in data else []
        items.append({
            "source": "google_trends",
            "keyword": kw,
            "trend": json.dumps(series),  # JSON pour compatibilité CSV
        })
    return items


def fetch_social_scrape(urls: List[str]) -> List[Dict[str, str]]:
    """Scrape léger des balises <title> et texte brut de pages web."""
    items = []
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            items.append({
                "source": url,
                "title": soup.title.string.strip() if soup.title else "",
                "url": url,
                "published": "",
                "snippet": soup.get_text(strip=True)[:200],
            })
        except Exception as e:
            logger.warning(f"[veille] Erreur scraping {url}: {e}")
    return items


def fetch_all_sources(
    rss_urls: Optional[List[str]] = None,
    trend_terms: Optional[List[str]] = None,
    social_urls: Optional[List[str]] = None
) -> List[Dict[str, str]]:
    """Fusionne toutes les sources de veille en une seule liste."""
    rss_urls = rss_urls or ["https://example.com/feed.xml"]
    trend_terms = trend_terms or ["marketing", "influence"]
    social_urls = social_urls or ["https://example.com"]

    items = []
    items += fetch_rss(rss_urls)
    items += fetch_google_trends(trend_terms)
    items += fetch_social_scrape(social_urls)
    return items


def save_to_csv(items: List[Dict[str, str]], path: str) -> None:
    """Sauvegarde la veille au format CSV."""
    if not items:
        logger.warning("Aucun item à sauvegarder.")
        return

    fieldnames = sorted({key for it in items for key in it.keys()})
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)


if __name__ == "__main__":
    # Test rapide pour usage direct
    all_items = fetch_all_sources()
    save_to_csv(all_items, "veille_export.csv")
    print(f"[OK] {len(all_items)} éléments sauvegardés dans veille_export.csv")

