import sys
from pathlib import Path

# On ajoute la racine du dépôt au PYTHONPATH pour importer nos modules non installés
depot_root = Path(__file__).parent.parent.resolve()
if str(depot_root) not in sys.path:
    sys.path.insert(0, str(depot_root))

# -------- Fixture principale pour test_parser ------------
import subprocess
import shutil
import pytest

@pytest.fixture(scope="session")
def generated_brief(tmp_path_factory):
    txt = tmp_path_factory.mktemp("dynamic") / "brief.txt"
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
    pdf = tmp_path_factory.mktemp("dynamic") / "brief.pdf"
    subprocess.run([
        sys.executable, "scripts/generate_brief_pdf.py",
        "--input", str(txt),
        "--output", str(pdf)
    ], check=True)
    return str(pdf)

# ---- Fixture auto qui alimente tests/samples/brief_sample.pdf ----
@pytest.fixture(scope="session", autouse=True)
def ensure_static_sample(tmp_path_factory):
    sample_dir = Path("tests/samples")
    sample_dir.mkdir(parents=True, exist_ok=True)

    # créer un txt minimal
    txt = tmp_path_factory.mktemp("static") / "brief.txt"
    txt.write_text(
        "TITRE STATIC\n\n"
        "Problème\n"
        "Brief statique pour les tests d’intégration.\n\n"
        "Objectifs\n"
        "Test statique.\n\n"
        "KPIs\n"
        "- TEST1\n",
        encoding="utf-8"
    )

    # générer le PDF statique
    pdf = tmp_path_factory.mktemp("static") / "brief_static.pdf"
    subprocess.run([
        sys.executable, "scripts/generate_brief_pdf.py",
        "--input", str(txt),
        "--output", str(pdf)
    ], check=True)

    # copier sous tests/samples/brief_sample.pdf
    dest = sample_dir / "brief_sample.pdf"
    shutil.copy(str(pdf), str(dest))
    return None
