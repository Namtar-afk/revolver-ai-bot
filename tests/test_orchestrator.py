import pytest

from bot.orchestrator import process_brief


def test_process_brief_fallback(tmp_path, monkeypatch):
    # Simule extract_brief_sections qui ne renvoie rien
    monkeypatch.setattr("bot.orchestrator.extract_brief_sections", lambda text: {})
    # On simule aussi un PDF « vide » pour bypasser extract_text
    monkeypatch.setattr(
        "bot.orchestrator.extract_text_from_pdf", lambda path: "dummy text"
    )

    out = process_brief(str(tmp_path / "dummy.pdf"))
    # Les clés obligatoires doivent toutes exister
    assert set(out) >= {"titre", "problème", "objectifs", "kpis"}
    # KPI doit être une liste non vide
    assert isinstance(out["kpis"], list) and len(out["kpis"]) >= 1
