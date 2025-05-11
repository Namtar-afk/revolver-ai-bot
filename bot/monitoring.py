import feedparser
from pytrends.request import TrendReq
import requests
from bs4 import BeautifulSoup
import csv
import logging
import json

logger = logging.getLogger(__name__)

def fetch_rss(urls):
    items = []
    for url in urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            items.append({
                "source": url,
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "published": entry.get("published", ""),
                "snippet": entry.get("summary", ""),
            })
    return items

def fetch_google_trends(kw_list):
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
            "trend": json.dumps(series),  # sérialisation JSON de la liste
        })
    return items

def fetch_social_scrape(urls):
    items = []
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            items.append({
                "source": url,
                "title": soup.title.string if soup.title else "",
                "url": url,
                "published": "",
                "snippet": soup.get_text()[:200].strip(),
            })
        except Exception as e:
            logger.warning(f"[veille] Erreur scraping {url}: {e}")
    return items

def fetch_all_sources():
    # TODO : remplacer par tes vraies listes de sources
    rss_urls    = ["https://example.com/feed.xml"]
    trend_terms = ["marketing", "influence"]
    social_urls = ["https://example.com"]

    items = []
    items += fetch_rss(rss_urls)
    items += fetch_google_trends(trend_terms)
    items += fetch_social_scrape(social_urls)
    return items

def save_to_csv(items, path):
    if not items:
        logger.warning("Aucun item à sauvegarder.")
        return
    # union de toutes les clés
    fieldnames = sorted({ key for it in items for key in it.keys() })
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)
