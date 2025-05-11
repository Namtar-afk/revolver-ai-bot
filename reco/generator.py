#!/usr/bin/env python3
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

def generate_recommendation(
    brief: BriefReminder,
    trends: List[StateOfPlaySection]
) -> DeckData:
    """
    Stub générique de génération de recommandations.
    Reçoit un brief et une liste d'insights (StateOfPlaySection) et
    produit un DeckData avec la structure standard:

    1. Brief Reminder
    2. Brand Overview
    3. State of Play
    4. 3 x Ideas
    5. Timeline
    6. Budget

    À remplacer par des vrais appels LLM.
    """
    # 1. Brief Reminder (on réutilise le modèle reçu)
    brief_reminder = brief

    # 2. Brand Overview (vide / générique)
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

    # 3. State of Play (on réutilise les trends fournies)
    state_of_play = trends

    # 4. Trois idées génériques
    ideas = [
        Idea(title="Idée #1", body="À remplir : proposition stratégique 1."),
        Idea(title="Idée #2", body="À remplir : proposition stratégique 2."),
        Idea(title="Idée #3", body="À remplir : proposition stratégique 3."),
    ]

    # 5. Timeline – étapes clés génériques
    timeline = [
        Milestone(milestone="Étape 1", date="YYYY-MM-DD"),
        Milestone(milestone="Étape 2", date="YYYY-MM-DD"),
    ]

    # 6. Budget – postes génériques
    budget = [
        BudgetItem(item="Production", amount=0.0),
        BudgetItem(item="Veille & Analyse", amount=0.0),
    ]

    return DeckData(
        brief_reminder=brief_reminder,
        brand_overview=brand_overview,
        state_of_play=state_of_play,
        ideas=ideas,
        timeline=timeline,
        budget=budget,
    )
