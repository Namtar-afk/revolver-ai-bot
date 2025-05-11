#!/usr/bin/env python3
import os
import pathlib
from typing import List

import openai
from reco.models import (
    DeckData,
    BriefReminder,
    BrandOverview,
    StateOfPlaySection,
    Idea,
    Milestone,
    BudgetItem,
    TrendItem,
)

# Retarder la validation de la clé API au moment de l'appel LLM
_openai_api_key = os.getenv("OPENAI_API_KEY", "")


def _ensure_api_key():
    if not _openai_api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable")
    openai.api_key = _openai_api_key


def _call_llm(prompt_path: str, context: str) -> str:
    """
    Lit le prompt depuis le fichier Markdown, injecte le contexte et renvoie la réponse brute du LLM.
    """
    _ensure_api_key()
    template = pathlib.Path(prompt_path).read_text(encoding="utf-8")
    full_prompt = f"{template}\n\nContexte :\n{context}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": full_prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def generate_insights(brief: BriefReminder, trends: List[TrendItem]) -> List[Idea]:
    # TODO : appeler prompt/insights.md via _call_llm pour remplir la liste
    return []


def generate_hypotheses(brief: BriefReminder, trends: List[TrendItem]) -> List[Idea]:
    # TODO : appeler prompt/hypotheses.md
    return []


def generate_kpis(brief: BriefReminder, trends: List[TrendItem]) -> List[Idea]:
    # TODO : appeler prompt/kpis.md
    return []


def generate_executive_summary(brief: BriefReminder, trends: List[TrendItem]) -> str:
    # TODO : appeler prompt/executive_summary.md
    return ""


def generate_ideas(brief: BriefReminder, trends: List[TrendItem]) -> List[Idea]:
    # stub : renvoie une liste vide pour les tests
    return []


def generate_timeline(brief: BriefReminder, trends: List[TrendItem]) -> List[Milestone]:
    # stub : renvoie une liste vide pour les tests
    return []


def generate_budget(brief: BriefReminder, trends: List[TrendItem]) -> List[BudgetItem]:
    # stub : renvoie une liste vide pour les tests
    return []


def generate_recommendation(
    brief: BriefReminder,
    trends: List[TrendItem]
) -> DeckData:
    """
    Orchestrateur :
      - Convertit BriefReminder + tendances en DeckData
      - Appelle generate_insights(), generate_hypotheses(), generate_kpis(), generate_executive_summary(),
        generate_ideas(), generate_timeline(), generate_budget()
      - Renvoie un DeckData complet
    """
    insights = generate_insights(brief, trends)
    hypotheses = generate_hypotheses(brief, trends)
    kpis = generate_kpis(brief, trends)
    summary = generate_executive_summary(brief, trends)
    ideas = generate_ideas(brief, trends)
    timeline = generate_timeline(brief, trends)
    budget = generate_budget(brief, trends)

    # Stub minimal pour brand_overview et state_of_play
    brand_overview = BrandOverview(
        description_paragraphs=[],
        competitive_positioning={"axes": [], "brands": []},
        persona={"heading": "", "bullets": []},
        top3_competitor_actions=[]
    )
    state_of_play = [StateOfPlaySection(theme=t.theme, evidence=[]) for t in trends]

    return DeckData(
        brief_reminder=brief,
        brand_overview=brand_overview,
        state_of_play=state_of_play,
        ideas=ideas,
        timeline=timeline,
        budget=budget,
    )
