import sys
import subprocess
from pathlib import Path

def test_slack_cli_veille(tmp_path, monkeypatch):
    # Prépare un dossier data/ à la racine du projet
    project_root = Path(__file__).parent.parent.resolve()
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)

    # S'assure que Python voit bien le projet
    monkeypatch.setenv("PYTHONPATH", str(project_root))

    # Invoque le module bot.slack_handler en mode veille
    cmd = [
        sys.executable,
        "-m", "bot.slack_handler",
        "--veille"
    ]
    rc = subprocess.run(
        cmd,
        cwd=str(project_root),
        capture_output=True,
        text=True
    )

    assert rc.returncode == 0, rc.stderr
    assert "items sauvegardés" in rc.stdout
