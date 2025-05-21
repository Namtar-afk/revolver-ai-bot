import subprocess
from parser.pdf_parser import extract_text_from_pdf

import pytest


@pytest.mark.parametrize(
    "script,params",
    [("generate_sample_pdf.py", None), ("make_valid_test_pdf.py", {"pages": 3})],
)
def test_pdf_text_extraction(tmp_path, script, params):
    txt = tmp_path / "b.txt"
    txt.write_text(
        "TITRE\n\nProblème\nTest.\n\nObjectifs\nOk\n\nKPIs\n- +1", encoding="utf-8"
    )
    pdf = tmp_path / "b.pdf"
    cmd = ["python", "scripts/" + script, "-i", str(txt), "-o", str(pdf)]
    if params:
        for k, v in params.items():
            cmd += [f"--{k}", str(v)]
    subprocess.run(cmd, check=True)
    text = extract_text_from_pdf(str(pdf))
    assert text and "Problème" in text
