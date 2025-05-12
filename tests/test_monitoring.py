import os
import csv
import pytest
from bot.monitoring import fetch_rss, save_to_csv


def test_fetch_rss_empty():
    """
    Teste l'extraction depuis un flux RSS local (fixtures).
    """
    items = fetch_rss(["tests/fixtures/sample.rss"])
    assert isinstance(items, list)
    assert items, "Le flux RSS est vide"
    assert "title" in items[0], "Le champ 'title' est manquant"
    assert items[0]["title"] == "Article Test"


def test_save_to_csv(tmp_path):
    """
    Teste l'écriture d'un CSV à partir d'une liste de dictionnaires.
    """
    dummy = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    path = tmp_path / "out.csv"
    save_to_csv(dummy, str(path))

    assert path.exists(), "Le fichier CSV n'a pas été créé"

    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 2
    assert rows[0]["a"] == "1"
    assert rows[1]["b"] == "4"
