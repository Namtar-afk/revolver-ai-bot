import os
import subprocess

def test_cli_report(tmp_path):
    out = tmp_path / "r.pptx"
    res = subprocess.run(
        ["python", "run_parser.py", "--report", str(out)],
        capture_output=True,
        text=True
    )
    assert res.returncode == 0
    assert out.exists()
