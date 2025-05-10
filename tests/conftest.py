import subprocess, shutil
from pathlib import Path
import pytest

@pytest.fixture(scope="session")
def generated_brief(tmp_path_factory):
    # Génération d’un brief “dynamique” pour test_parser
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
        "python", "scripts/generate_sample_pdf.py",
        "-i", str(txt), "-o", str(pdf)
    ], check=True)
    return str(pdf)

@pytest.fixture(scope="session", autouse=True)
def ensure_static_briefs(tmp_path_factory):
    """
    Génère les trois briefs statiques attendus par
    test_extract_text_from_pdf_schema.py et test_integration.py
    """
    sample_dir = Path("tests/samples")
    sample_dir.mkdir(parents=True, exist_ok=True)

    # 1) base .txt commun
    base_txt = tmp_path_factory.mktemp("static") / "brief.txt"
    base_txt.write_text(
        "TITRE STATIC\n\n"
        "Problème\n"
        "Brief pour tests statiques.\n\n"
        "Objectifs\n"
        "Test statique.\n\n"
        "KPIs\n"
        "- +5 éléments.\n",
        encoding="utf-8"
    )

    # 2) brief_simple.pdf  (1 page)
    pdf_simple = tmp_path_factory.mktemp("static") / "brief_simple.pdf"
    subprocess.run([
        "python", "scripts/generate_sample_pdf.py",
        "-i", str(base_txt), "-o", str(pdf_simple)
    ], check=True)
    shutil.copy(str(pdf_simple), str(sample_dir / "brief_simple.pdf"))

    # 3) brief_multi.pdf   (multi‐page via make_valid_test_pdf.py)
    pdf_multi = tmp_path_factory.mktemp("static") / "brief_multi.pdf"
    subprocess.run([
        "python", "scripts/make_valid_test_pdf.py",
        "-i", str(base_txt), "-o", str(pdf_multi), "-p", "4"
    ], check=True)
    shutil.copy(str(pdf_multi), str(sample_dir / "brief_multi.pdf"))

    # 4) brief_sample.pdf  (pour intégration CLI / email_handler / slack_handler)
    pdf_sample = tmp_path_factory.mktemp("static") / "brief_sample.pdf"
    subprocess.run([
        "python", "scripts/generate_sample_pdf.py",
        "-i", str(base_txt), "-o", str(pdf_sample)
    ], check=True)
    shutil.copy(str(pdf_sample), str(sample_dir / "brief_sample.pdf"))

    return None
