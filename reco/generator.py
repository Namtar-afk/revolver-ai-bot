#!/usr/bin/env python3
import openai
import pathlib
from typing import List

from reco.models import (
    DeckData,
    BriefReminder,
    BrandOverview,
    StateOfPlaySection,
    Idea,
    Milestone,
    BudgetItem,
    CompetitorActions,
    BrandPosition,
    Action,
)

# Chargez votre clé API dans une variable d’environnement, e.g. OPENAI_API_KEY
openai.api_key = "YOUR_API_KEY_HERE"


def _call_llm(prompt_path: str, context: str) -> str:
    """
    Lit le prompt depuis le fichier Markdown, injecte le contexte
    et renvoie la réponse brute du LLM.
    """
    template = pathlib.Path(prompt_path).read_text()
    full_prompt = f"{template}\n\nContexte :\n{context}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": full_prompt}]
    )
    return response.choices[0].message.content.strip()


def generate_recommendation(
    brief: BriefReminder,
    trends: List[StateOfPlaySection]
) -> DeckData:
    """
    Génère un DeckData complet à partir du brief et des trends.
    Appelle les sous-fonctions pour chaque partie du deck.
    """
    # 1. Brief Reminder
    brief_reminder = brief

    # 2. Brand Overview
    brand_overview = BrandOverview(
        description_paragraphs=[
            "À compléter : résumé de la perception et de l’histoire de la marque."
        ],
        competitive_positioning={
            "axes": ["Axe X", "Axe Y"],
            "brands": [
                BrandPosition(name="Marque A", x=5.0, y=5.0),
                BrandPosition(name="Marque B", x=6.0, y=4.0),
                BrandPosition(name=brief.title, x=4.5, y=6.0),
            ],
        },
        persona={
            "heading": "À compléter : personae cible",
            "bullets": [
                "Caractéristique 1 de la cible.",
                "Caractéristique 2 de la cible.",
                "Caractéristique 3 de la cible.",
            ],
        },
        top3_competitor_actions=[
            CompetitorActions(
                competitor="Concurrent 1",
                actions=[
                    Action(title="Action 1", desc="Description de l’action concurrente."),
                    Action(title="Action 2", desc="Description de l’action concurrente."),
                ]
            )
        ],
    )

    # 3. State of Play
    state_of_play = trends

    # Concaténez brief + trends pour le contexte LLM
    context = f"Brief : {brief.json()}\nTrends : {[t.json() for t in trends]}"

    # 4. Ideas via LLM
    ideas_raw = _call_llm("prompts/ideas.md", context)
    # TODO : parser ideas_raw en List[Idea]
    ideas: List[Idea] = []

    # 5. Timeline via LLM
    timeline_raw = _call_llm("prompts/timeline.md", context)
    # TODO : parser timeline_raw en List[Milestone]
    timeline: List[Milestone] = []

    # 6. Budget via LLM
    budget_raw = _call_llm("prompts/budget.md", context)
    # TODO : parser budget_raw en List[BudgetItem]
    budget: List[BudgetItem] = []

    return DeckData(
        brief_reminder=brief_reminder,
        brand_overview=brand_overview,
        state_of_play=state_of_play,
        ideas=ideas,
        timeline=timeline,
        budget=budget,
    )


# Fonctions séparées si besoin

def generate_ideas(analysis, trends) -> List[Idea]:
    context = f"Analysis: {analysis.json()}\nTrends: {[t.json() for t in trends]}"
    ideas_raw = _call_llm("prompts/ideas.md", context)
    # TODO : parser ideas_raw
    return []

def generate_timeline(analysis, trends) -> List[Milestone]:
    context = f"Analysis: {analysis.json()}\nTrends: {[t.json() for t in trends]}"
    timeline_raw = _call_llm("prompts/timeline.md", context)
    # TODO : parser timeline_raw
    return []

def generate_budget(analysis, trends) -> List[BudgetItem]:
    context = f"Analysis: {analysis.json()}\nTrends: {[t.json() for t in trends]}"
    budget_raw = _call_llm("prompts/budget.md", context)
    # TODO : parser budget_raw
    return []
