import subprocess
import sys

def test_run_parser_cli():
    """Vérifie que le CLI `run_parser.py` renvoie un brief valide."""
    cmd = [sys.executable, "run_parser.py"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Échec CLI: {result.stderr}"
    assert "Brief valide" in result.stdout or "Validation JSON réussie" in result.stdout