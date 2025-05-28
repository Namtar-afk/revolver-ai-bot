# tests/test_generator_sections.py
import json

import pytest

from reco import generator
from reco.models import (
    BrandOverview,
    BriefReminder,
    BudgetItem,
    DeckData,
    Idea,
    Milestone,
    StateOfPlaySection,
    TrendItem,
)


# fixtures minimalistes
@pytest.fixture
def dummy_brief():
    return BriefReminder(
        title="Projet Test",
        objectives=["Obj1", "Obj2"],
        internal_reformulation="Reformulation",
        summary="Résumé test",
    )


@pytest.fixture
def dummy_trends():
    return [
        TrendItem(
            date="2025-01-01",
            source="SourceA",
            title="Tendance A",
            snippet="Snippet A",
            theme="Thème A",
            evidence=["Ev1", "Ev2"],
        ),
        TrendItem(
            date="2025-02-01",
            source="SourceB",
            title="Tendance B",
            snippet="Snippet B",
            theme="Thème B",
            evidence=["Ev3"],
        ),
    ]


# utilitaire pour stubber _call_llm
def stub_llm(monkeypatch, return_value):
    monkeypatch.setattr(generator, "_call_llm", lambda *args, **kwargs: return_value)


def test_generate_insights(monkeypatch, dummy_brief, dummy_trends):
    stub_llm(monkeypatch, "- Idea1\n- Idea2\n")
    res = generator.generate_insights(dummy_brief, dummy_trends)
    assert isinstance(res, list)
    assert all(isinstance(i, Idea) for i in res)
    assert [i.label for i in res] == ["Idea1", "Idea2"]


def test_generate_hypotheses(monkeypatch, dummy_brief, dummy_trends):
    stub_llm(monkeypatch, "1. Hyp1\n2. Hyp2")
    res = generator.generate_hypotheses(dummy_brief, dummy_trends)
    assert [h.label for h in res] == ["Hyp1", "Hyp2"]


def test_generate_kpis(monkeypatch, dummy_brief, dummy_trends):
    stub_llm(monkeypatch, "* KPI1\n* KPI2")
    res = generator.generate_kpis(dummy_brief, dummy_trends)
    assert [k.label for k in res] == ["KPI1", "KPI2"]


def test_generate_executive_summary(monkeypatch, dummy_brief, dummy_trends):
    stub_llm(monkeypatch, "Ceci est un résumé.")
    res = generator.generate_executive_summary(dummy_brief, dummy_trends)
    assert isinstance(res, str)
    assert "résumé" in res.lower()


def test_generate_ideas(monkeypatch, dummy_brief, dummy_trends):
    stub_llm(monkeypatch, "Idea A line\nIdea B line\n\n")
    res = generator.generate_ideas(dummy_brief, dummy_trends)
    assert [i.label for i in res] == ["Idea A line", "Idea B line"]


def test_generate_timeline(monkeypatch, dummy_brief, dummy_trends):
    stub_llm(monkeypatch, "2025-03-01: Kick-off\n2025-06-01: Go-live")
    res = generator.generate_timeline(dummy_brief, dummy_trends)
    assert isinstance(res, list)
    assert all(isinstance(m, Milestone) for m in res)
    assert [(m.deadline, m.label) for m in res] == [
        ("2025-03-01", "Kick-off"),
        ("2025-06-01", "Go-live"),
    ]


def test_generate_budget(monkeypatch, dummy_brief, dummy_trends):
    stub_llm(
        monkeypatch,
        "Production – €10000 – tournage\nDigital – €5000 – ads\nInvalid line",
    )
    res = generator.generate_budget(dummy_brief, dummy_trends)
    assert all(isinstance(b, BudgetItem) for b in res)
    assert [(b.category, b.estimate, b.comment) for b in res] == [
        ("Production", 10000.0, "tournage"),
        ("Digital", 5000.0, "ads"),
    ]


def test_generate_brand_overview_valid_json(monkeypatch, dummy_brief, dummy_trends):
    payload = {
        "description_paragraphs": ["Par1", "Par2"],
        "competitive_positioning": {"axes": ["A"], "brands": ["B"]},
        "persona": {"heading": ["H"], "bullets": ["b1"]},
        "top3_competitor_actions": ["Act1", "Act2", "Act3"],
    }
    stub_llm(monkeypatch, json.dumps(payload))
    res = generator.generate_brand_overview(dummy_brief, dummy_trends)
    assert isinstance(res, BrandOverview)
    assert res.description_paragraphs == ["Par1", "Par2"]
    assert res.competitive_positioning["axes"] == ["A"]


def test_generate_brand_overview_fallback(monkeypatch, dummy_brief, dummy_trends):
    stub_llm(monkeypatch, "not a json")
    res = generator.generate_brand_overview(dummy_brief, dummy_trends)
    assert res.description_paragraphs == []
    assert res.competitive_positioning == {"axes": [], "brands": []}


def test_generate_state_of_play(monkeypatch, dummy_brief, dummy_trends):
    stub_llm(monkeypatch, "Theme: X\n- e1\n- e2\nTheme: Y\n- z1")
    res = generator.generate_state_of_play(dummy_brief, dummy_trends)
    assert isinstance(res, list)
    assert res[0] == StateOfPlaySection(theme="X", evidence=["e1", "e2"])
    assert res[1].theme == "Y"


def test_generate_recommendation(monkeypatch, dummy_brief, dummy_trends):
    # on stubbe tous les appels LLM pour ne tester que l'assemblage
    stub_llm(monkeypatch, "- A\n- B")
    deck = generator.generate_recommendation(dummy_brief, dummy_trends)
    assert isinstance(deck, DeckData)
    # les sections lists doivent être cohérentes
    assert all(isinstance(i, Idea) for i in deck.insights)
    assert isinstance(deck.executive_summary, str)
    assert deck.trends == dummy_trends
