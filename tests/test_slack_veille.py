import subprocess
import sys

def test_slack_cli_veille(tmp_path):
    # s'assure que le dossier data/ existe
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    # on lance la commande dans le cwd du projet
    cmd = [
        sys.executable,
        "bot/slack_handler.py",
        "--veille"
    ]
    rc = subprocess.run(cmd, cwd=str(tmp_path.parent), capture_output=True, text=True)
    assert rc.returncode == 0, rc.stderr
    assert "Veille lancée" in rc.stdout
