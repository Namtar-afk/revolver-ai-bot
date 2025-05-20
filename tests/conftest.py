import sys
from pathlib import Path
import subprocess
import shutil
import pytest

# -----------------------------------------------------------------------------
# 🔧 1. Ajout du répertoire racine du dépôt au PYTHONPATH pour les imports locaux
# -----------------------------------------------------------------------------
depot_root = Path(__file__).resolve().parent.parent
if str(depot_root) not in sys.path:
    sys.path.insert(0, str(depot_root))


# -----------------------------------------------------------------------------
# 📄 2. Fixture principale : génère un brief PDF dynamique pour les tests
# -----------------------------------------------------------------------------
@pytest.fixture(scope="session")
def generated_brief(tmp_path_factory):
    """
    Génère un fichier PDF de brief à partir d’un fichier texte temporaire.
    Utilisé pour les tests fonctionnels de parsing sur un brief dynamique.
    """
    # Création du fichier .txt temporaire
    txt = tmp_path_factory.mktemp("dynamic") / "brief.txt"
    txt.write_text(
        "TITRE D'EXEMPLE\n\n"
        "Problème\nLe client manque de notoriété.\n\n"
        "Objectifs\n1. Générer de la visibilité.\n\n"
        "KPIs\n- +10% d'engagement.\n",
        encoding="utf-8"
    )

    # Fichier PDF généré à partir du texte
    pdf = tmp_path_factory.mktemp("dynamic") / "brief.pdf"
    subprocess.run([
        sys.executable, "scripts/generate_brief_pdf.py",
        "--input", str(txt),
        "--output", str(pdf)
    ], check=True)

    return str(pdf)


# -----------------------------------------------------------------------------
# 📄 3. Fixture automatique (autouse=True) : crée un brief statique partagé
# -----------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def ensure_static_sample(tmp_path_factory):
    """
    Génère automatiquement un fichier PDF `brief_sample.pdf` dans tests/samples.
    Utilisé comme référence pour les tests d’intégration.
    """
    # Répertoire cible pour les fichiers de test
    sample_dir = Path("tests/samples")
    sample_dir.mkdir(parents=True, exist_ok=True)

    # Création du fichier .txt statique
    txt = tmp_path_factory.mktemp("static") / "brief.txt"
    txt.write_text(
        "TITRE STATIC\n\n"
        "Problème\nBrief statique pour les tests d’intégration.\n\n"
        "Objectifs\nTest statique.\n\n"
        "KPIs\n- TEST1\n",
        encoding="utf-8"
    )

    # PDF généré
    pdf = tmp_path_factory.mktemp("static") / "brief_static.pdf"
    subprocess.run([
        sys.executable, "scripts/generate_brief_pdf.py",
        "--input", str(txt),
        "--output", str(pdf)
    ], check=True)

    # Copie vers tests/samples/brief_sample.pdf
    dest = sample_dir / "brief_sample.pdf"
    shutil.copy(str(pdf), str(dest))

