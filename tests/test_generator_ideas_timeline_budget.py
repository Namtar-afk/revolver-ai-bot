import pytest

from reco.generator import generate_budget, generate_ideas, generate_timeline
from reco.models import BriefReminder, BudgetItem, Idea, Milestone


@pytest.fixture
def sample_brief():
    return BriefReminder(
        title="Titre test",
        summary="Résumé test",
        objectives=["Obj1", "Obj2"],
        internal_reformulation="Reformulation interne ici",
    )


@pytest.fixture
def sample_trends():
    # Pour valider la signature, on peut utiliser une liste vide
    return []


def test_generate_ideas_signature(sample_brief, sample_trends):
    out = generate_ideas(sample_brief, sample_trends)
    assert isinstance(out, list)
    if out:
        assert isinstance(out[0], Idea)


def test_generate_timeline_signature(sample_brief, sample_trends):
    out = generate_timeline(sample_brief, sample_trends)
    assert isinstance(out, list)
    if out:
        assert isinstance(out[0], Milestone)


def test_generate_budget_signature(sample_brief, sample_trends):
    out = generate_budget(sample_brief, sample_trends)
    assert isinstance(out, list)
    if out:
        assert isinstance(out[0], BudgetItem)
