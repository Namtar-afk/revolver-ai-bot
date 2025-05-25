"""
Pytest fixtures for generating dynamic and static sample briefs.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# Ensure project root is on PYTHONPATH for imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def generated_brief(tmp_path_factory):
    """
    Generate a dynamic PDF brief from a temporary text file.
    Returns the path to the generated PDF.
    """
    # Create temporary text input
    txt_file = tmp_path_factory.mktemp("dynamic") / "brief.txt"
    txt_content = (
        "TITRE D'EXEMPLE\n\n"
        "Problème\nLe client manque de notoriété.\n\n"
        "Objectifs\n1. Générer de la visibilité.\n\n"
        "KPIs\n- +10% d'engagement.\n"
    )
    txt_file.write_text(txt_content, encoding="utf-8")

    # Generate PDF via script
    pdf_file = tmp_path_factory.mktemp("dynamic") / "brief.pdf"
    subprocess.run(
        [
            sys.executable,
            "scripts/generate_brief_pdf.py",
            "--input",
            str(txt_file),
            "--output",
            str(pdf_file),
        ],
        check=True,
    )
    return str(pdf_file)


@pytest.fixture(scope="session", autouse=True)
def ensure_static_sample(tmp_path_factory):
    """
    Create and copy a static sample PDF brief for integration tests.
    The static file is placed in tests/samples/brief_sample.pdf.
    """
    sample_dir = Path(__file__).parent / "samples"
    sample_dir.mkdir(parents=True, exist_ok=True)

    txt_file = tmp_path_factory.mktemp("static") / "brief.txt"
    txt_content = (
        "TITRE STATIC\n\n"
        "Problème\nBrief statique pour les tests d’intégration.\n\n"
        "Objectifs\nTest statique.\n\n"
        "KPIs\n- TEST1\n"
    )
    txt_file.write_text(txt_content, encoding="utf-8")

    pdf_file = tmp_path_factory.mktemp("static") / "brief_static.pdf"
    subprocess.run(
        [
            sys.executable,
            "scripts/generate_brief_pdf.py",
            "--input",
            str(txt_file),
            "--output",
            str(pdf_file),
        ],
        check=True,
    )

    dest = sample_dir / "brief_sample.pdf"
    shutil.copy(str(pdf_file), str(dest))
