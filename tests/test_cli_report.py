import os
import subprocess


def test_cli_report(tmp_path):
    """
    Teste la génération d’un fichier PPTX à partir du CLI complet.
    """
    out = tmp_path / "r.pptx"

    res = subprocess.run(
        ["python", "run_parser.py", "--report", str(out)],
        capture_output=True,
        text=True
    )

    print("\n[STDOUT]\n", res.stdout)
    print("\n[STDERR]\n", res.stderr)

    assert res.returncode == 0, f"Échec CLI : {res.stderr}"
    assert out.exists(), "Le fichier PPTX attendu n’a pas été généré"
