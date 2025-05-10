import subprocess
from pathlib import Path
import pytest

@pytest.fixture(scope="session")
def generated_brief(tmp_path_factory):
    # Création d’un mini‐brief texte
    txt = tmp_path_factory.mktemp("data") / "brief.txt"
    txt.write_text(
        "TITRE D'EXEMPLE\n\n"
        "Problème\n"
        "Le client manque de notoriété.\n\n"
        "Objectifs\n"
        "1. Générer de la visibilité.\n\n"
        "KPIs\n"
        "- +10% d'engagement.\n",
        encoding="utf-8"
    )
    pdf = tmp_path_factory.mktemp("data") / "brief.pdf"
    subprocess.run([
        "python", "scripts/generate_brief_pdf.py",
        "--input", str(txt),
        "--output", str(pdf)
    ], check=True)
    return str(pdf)
