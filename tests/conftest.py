import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# Ajout du dossier racine au PYTHONPATH
depot_root = Path(__file__).resolve().parent.parent
if str(depot_root) not in sys.path:
    sys.path.insert(0, str(depot_root))


@pytest.fixture(scope="session")
def generated_brief(tmp_path_factory):
    txt = tmp_path_factory.mktemp("dynamic") / "brief.txt"
    txt.write_text(
        "TITRE D'EXEMPLE\n\n"
        "Problème\nLe client manque de notoriété.\n\n"
        "Objectifs\n1. Générer de la visibilité.\n\n"
        "KPIs\n- +10% d'engagement.\n",
        encoding="utf-8",
    )
    pdf = tmp_path_factory.mktemp("dynamic") / "brief.pdf"
    subprocess.run(
        [
            sys.executable,
            "scripts/generate_brief_pdf.py",
            "--input",
            str(txt),
            "--output",
            str(pdf),
        ],
        check=True,
    )
    return str(pdf)


@pytest.fixture(scope="session", autouse=True)
def ensure_static_sample(tmp_path_factory):
    sample_dir = Path("tests/samples")
    sample_dir.mkdir(parents=True, exist_ok=True)
    txt = tmp_path_factory.mktemp("static") / "brief.txt"
    txt.write_text(
        "TITRE STATIC\n\n"
        "Problème\nBrief statique pour les tests d’intégration.\n\n"
        "Objectifs\nTest statique.\n\n"
        "KPIs\n- TEST1\n",
        encoding="utf-8",
    )
    pdf = tmp_path_factory.mktemp("static") / "brief_static.pdf"
    subprocess.run(
        [
            sys.executable,
            "scripts/generate_brief_pdf.py",
            "--input",
            str(txt),
            "--output",
            str(pdf),
        ],
        check=True,
    )
    dest = sample_dir / "brief_sample.pdf"
    shutil.copy(str(pdf), str(dest))
