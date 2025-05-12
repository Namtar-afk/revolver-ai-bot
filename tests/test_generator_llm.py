import pytest
from reco import generator
from reco.models import BriefReminder, TrendItem, DeckData


@pytest.fixture
def dummy_brief():
    return BriefReminder(
        title="Lancement MycoBeauty",
        objectives=["Accroître notoriété", "Éduquer sur les bienfaits des champignons"],
        internal_reformulation="Créer une campagne innovante autour de l'univers fongique",
        summary="Campagne de lancement sur les réseaux sociaux + influence"
    )


@pytest.fixture
def dummy_trends():
    return [
        TrendItem(
            source="TikTok",
            title="Boom des skincare DIY",
            date="2025-05-10",
            snippet="Les routines naturelles explosent sur TikTok",
            theme="Naturalité",
            evidence=[]
        ),
        TrendItem(
            source="Instagram",
            title="Retour des champignons",
            date="2025-05-11",
            snippet="L'esthétique mycologique cartonne",
            theme="Esthétique fongique",
            evidence=[]
        )
    ]


@pytest.fixture
def fake_response():
    return "- Insight 1\n- Insight 2\n- Insight 3"


def test_generate_insights(monkeypatch, dummy_brief, dummy_trends, fake_response):
    monkeypatch.setattr(generator, "_call_llm", lambda path, ctx: fake_response)
    insights = generator.generate_insights(dummy_brief, dummy_trends)
    assert len(insights) == 3
    assert insights[0].label == "Insight 1"


def test_generate_hypotheses(monkeypatch, dummy_brief, dummy_trends, fake_response):
    monkeypatch.setattr(generator, "_call_llm", lambda path, ctx: fake_response)
    hypotheses = generator.generate_hypotheses(dummy_brief, dummy_trends)
    assert len(hypotheses) == 3
    assert hypotheses[1].label == "Insight 2"


def test_generate_kpis(monkeypatch, dummy_brief, dummy_trends, fake_response):
    monkeypatch.setattr(generator, "_call_llm", lambda path, ctx: fake_response)
    kpis = generator.generate_kpis(dummy_brief, dummy_trends)
    assert len(kpis) == 3
    assert all(k.label.startswith("Insight") for k in kpis)


def test_generate_summary(monkeypatch, dummy_brief, dummy_trends):
    summary_text = "Voici un résumé concis de la recommandation stratégique."
    monkeypatch.setattr(generator, "_call_llm", lambda path, ctx: summary_text)
    summary = generator.generate_executive_summary(dummy_brief, dummy_trends)
    assert summary == summary_text


def test_generate_recommendation(monkeypatch, dummy_brief, dummy_trends, fake_response):
    monkeypatch.setattr(generator, "_call_llm", lambda path, ctx: fake_response)
    reco = generator.generate_recommendation(dummy_brief, dummy_trends)
    assert isinstance(reco, DeckData)
    assert len(reco.insights) == 3
    assert len(reco.kpis) == 3
    assert isinstance(reco.executive_summary, str)
