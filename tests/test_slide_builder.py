import os
import tempfile

import pytest
from pptx import Presentation

from pptx_generator.slide_builder import build_ppt
from reco.models import (BrandOverview, BriefReminder, BudgetItem, DeckData,
                         Idea, Milestone, StateOfPlaySection)


@pytest.fixture
def minimal_deck():
    brief = BriefReminder(
        title="Test",
        objectives=["Obj1"],
        internal_reformulation="Reformulation",
        summary="Résumé",
    )
    brand = BrandOverview(
        description_paragraphs=["Desc"],
        competitive_positioning={"axes": [], "brands": []},
        persona={"heading": ["P"], "bullets": []},
        top3_competitor_actions=[],
    )
    deck = DeckData(
        brief_reminder=brief,
        brand_overview=brand,
        state_of_play=[StateOfPlaySection(theme="T", evidence=["ev1"])],
        insights=[Idea(label="I1", bullets=[])],
        hypotheses=[Idea(label="H1", bullets=[])],
        kpis=[Idea(label="K1", bullets=[])],
        executive_summary="Exec",
        ideas=[Idea(label="Idea1", bullets=[])],
        timeline=[Milestone(label="M1", deadline="2025-06-01")],
        budget=[BudgetItem(category="B1", estimate=100.0, comment="C1")],
    )
    return deck


def test_build_ppt_creates_file(minimal_deck):
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "test.pptx")
        build_ppt(minimal_deck, out)
        assert os.path.exists(out)
        # on peut vérifier que c'est un .pptx valide
        prs = Presentation(out)
        # attendre au moins 6 slides + titre
        assert len(prs.slides) >= 6
