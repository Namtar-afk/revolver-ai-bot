import os
import csv
import pytest
from bot.monitoring import fetch_rss, save_to_csv


def test_fetch_rss_empty():
    """
    Teste l'extraction depuis un flux RSS local (fixtures).
    Vérifie que le contenu est bien parsé et conforme.
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
    dummy_data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    output_path = tmp_path / "out.csv"
    save_to_csv(dummy_data, str(output_path))

    assert output_path.exists(), "Le fichier CSV n'a pas été créé"

    with open(output_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 2, "Le nombre de lignes est incorrect"
    assert rows[0]["a"] == "1", "La première valeur de 'a' est incorrecte"
    assert rows[1]["b"] == "4", "La deuxième valeur de 'b' est incorrecte"

