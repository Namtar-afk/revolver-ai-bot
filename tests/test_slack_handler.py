import subprocess
import sys
import shutil

def test_run_parser_cli():
    result = subprocess.run(
        [sys.executable, "run_parser.py", "--brief", "tests/samples/brief_sample.pdf"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Erreur CLI : {result.stderr}"
    assert '"title": "Brief extrait automatiquement"' in result.stdout or "Résumé" in result.stdout


def test_slack_simulator(capsys):
    from bot.slack_handler import simulate_upload
    simulate_upload()
    out, _ = capsys.readouterr()
    assert "Brief extrait automatiquement" in out or "Résumé" in out


def test_email_handler(tmp_path, capsys):
    inbox_dir = tmp_path / "inbox"
    inbox_dir.mkdir()

    sample_pdf = "tests/samples/brief_sample.pdf"
    dest_pdf = inbox_dir / "brief1.pdf"
    shutil.copy(sample_pdf, dest_pdf)

    import bot.email_handler as eh
    eh.INBOX_DIR = str(inbox_dir)

    eh.handle_inbox()
    out, _ = capsys.readouterr()
    assert "-- PROBLEM --" in out.upper() or "-- OBJECTIF --" in out.upper()
    assert "-- KPIS --" in out.upper()

