import pytest

from reco.generator import (generate_executive_summary, generate_insights,
                            generate_kpis, generate_recommendation)
from reco.models import BriefReminder, DeckData, Idea, TrendItem


@pytest.fixture
def sample_brief():
    return BriefReminder(
        title="Campagne 2025",
        objectives=["Obj1", "Obj2"],
        internal_reformulation="Reformulation interne ici",
        summary="Résumé auto pour les prompts",
    )


@pytest.fixture
def sample_trends():
    return [
        TrendItem(
            source="RSS",
            title="Titre de tendance",
            date="2025-05-12",
            snippet="Résumé de la tendance détectée",
            theme="Tendance",
            evidence=["https://source.example.com/article-trend"],
        )
    ]


@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")


@pytest.fixture(autouse=True)
def mock_llm(monkeypatch):
    monkeypatch.setattr(
        "reco.generator._call_llm", lambda path, ctx: "- Insight 1\n- Insight 2"
    )


def test_generate_insights_signature(sample_brief, sample_trends):
    out = generate_insights(sample_brief, sample_trends)
    assert isinstance(out, list)
    assert len(out) == 2
    assert all(isinstance(i, Idea) for i in out)
    assert out[0].label == "Insight 1"


def test_generate_kpis_signature(sample_brief, sample_trends):
    out = generate_kpis(sample_brief, sample_trends)
    assert isinstance(out, list)
    assert len(out) == 2
    assert all(isinstance(k, Idea) for k in out)


def test_generate_executive_summary_signature(sample_brief, sample_trends):
    out = generate_executive_summary(sample_brief, sample_trends)
    assert isinstance(out, str)
    assert "Insight" in out or isinstance(out, str)


def test_generate_recommendation_returns_deckdata(sample_brief, sample_trends):
    out = generate_recommendation(sample_brief, sample_trends)
    assert isinstance(out, DeckData)
    assert isinstance(out.insights, list)
    assert all(isinstance(i, Idea) for i in out.insights)
    assert isinstance(out.executive_summary, str)
