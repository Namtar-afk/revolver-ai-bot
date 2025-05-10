import os, csv
import pytest
from bot.monitoring import fetch_rss, save_to_csv

def test_fetch_rss_empty():
    # un flux RSS factice dans tests/fixtures/sample.rss
    items = fetch_rss(["tests/fixtures/sample.rss"])
    assert isinstance(items, list)

def test_save_to_csv(tmp_path):
    dummy = [{"a":1,"b":2},{"a":3,"b":4}]
    path  = tmp_path / "out.csv"
    save_to_csv(dummy, str(path))
    with open(path) as f:
        reader = list(csv.DictReader(f))
    assert reader and reader[0]["a"] == "1"
