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

# Clé API différée à l'exécution
_openai_api_key = os.getenv("OPENAI_API_KEY", "")

def _ensure_api_key():
    if not _openai_api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable")
    openai.api_key = _openai_api_key

def _call_llm(prompt_path: str, context: str) -> str:
    """
    Lit un fichier Markdown de prompt, injecte le contexte, appelle l'API OpenAI et retourne la réponse.
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

def _build_context(brief: BriefReminder, trends: List[TrendItem]) -> str:
    lines = [f"# Brief\n{brief.summary}", "# Tendances"]
    for trend in trends:
        lines.append(f"- {trend.date} | {trend.source} : {trend.title}\n{trend.snippet}")
    return "\n".join(lines)

def _parse_list(text: str) -> List[str]:
    """
    Extrait une liste à puces d'un texte brut (format LLM).
    Gère "-", "*", "1.", etc.
    """
    lines = text.strip().splitlines()
    return [line.lstrip("-*0123456789. ").strip() for line in lines if line.strip()]

def generate_insights(brief: BriefReminder, trends: List[TrendItem]) -> List[Idea]:
    context = _build_context(brief, trends)
    raw = _call_llm("prompts/insights.md", context)
    return [Idea(label=item, bullets=[]) for item in _parse_list(raw)]

def generate_hypotheses(brief: BriefReminder, trends: List[TrendItem]) -> List[Idea]:
    context = _build_context(brief, trends)
    raw = _call_llm("prompts/hypotheses.md", context)
    return [Idea(label=item, bullets=[]) for item in _parse_list(raw)]

def generate_kpis(brief: BriefReminder, trends: List[TrendItem]) -> List[Idea]:
    context = _build_context(brief, trends)
    raw = _call_llm("prompts/kpis.md", context)
    return [Idea(label=item, bullets=[]) for item in _parse_list(raw)]

def generate_executive_summary(brief: BriefReminder, trends: List[TrendItem]) -> str:
    context = _build_context(brief, trends)
    return _call_llm("prompts/executive_summary.md", context)

def generate_ideas(brief: BriefReminder, trends: List[TrendItem]) -> List[Idea]:
    return []  # Stub

def generate_timeline(brief: BriefReminder, trends: List[TrendItem]) -> List[Milestone]:
    return []  # Stub

def generate_budget(brief: BriefReminder, trends: List[TrendItem]) -> List[BudgetItem]:
    return []  # Stub

def generate_recommendation(brief: BriefReminder, trends: List[TrendItem]) -> DeckData:
    """
    Orchestrateur principal : convertit brief + tendances en une recommandation complète (DeckData).
    """
    insights = generate_insights(brief, trends)
    hypotheses = generate_hypotheses(brief, trends)
    kpis = generate_kpis(brief, trends)
    summary = generate_executive_summary(brief, trends)
    ideas = generate_ideas(brief, trends)
    timeline = generate_timeline(brief, trends)
    budget = generate_budget(brief, trends)

    brand_overview = BrandOverview(
        description_paragraphs=[],
        competitive_positioning={"axes": [], "brands": []},
        persona={"heading": [""], "bullets": []},  # heading est une liste
        top3_competitor_actions=[],
    )

    state_of_play = [
        StateOfPlaySection(theme=t.theme, evidence=[]) for t in trends
    ]

    return DeckData(
        brief_reminder=brief,
        brand_overview=brand_overview,
        state_of_play=state_of_play,
        insights=insights,
        hypotheses=hypotheses,
        kpis=kpis,
        executive_summary=summary,
        ideas=ideas,
        timeline=timeline,
        budget=budget,
    )