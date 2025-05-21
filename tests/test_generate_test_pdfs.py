# tests/test_generate_test_pdfs.py

from generate_test_pdfs import generate_pdf


def test_generate_pdf_runs(tmp_path):
    output_file = tmp_path / "brief_test.pdf"
    generate_pdf(str(output_file))

    assert output_file.exists()
    assert output_file.stat().st_size > 0  # Vérifie que le fichier n'est pas vide
