import os

import pytest

from reco.generator import (
    generate_executive_summary,
    generate_hypotheses,
    generate_insights,
    generate_kpis,
    generate_recommendation,
)
from reco.models import BriefReminder, TrendItem


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
            evidence=[],
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


def test_generate_hypotheses_signature(sample_brief, sample_trends):
    out = generate_hypotheses(sample_brief, sample_trends)
    assert isinstance(out, list)
    assert len(out) == 2


def test_generate_kpis_signature(sample_brief, sample_trends):
    out = generate_kpis(sample_brief, sample_trends)
    assert isinstance(out, list)
    assert len(out) == 2


def test_generate_executive_summary_signature(sample_brief, sample_trends):
    out = generate_executive_summary(sample_brief, sample_trends)
    assert isinstance(out, str)
    assert "Insight" in out


def test_generate_recommendation_returns_deckdata(sample_brief, sample_trends):
    out = generate_recommendation(sample_brief, sample_trends)
    assert out.brief_reminder.title == "Campagne 2025"
    assert len(out.insights) == 2
    assert isinstance(out.executive_summary, str)
