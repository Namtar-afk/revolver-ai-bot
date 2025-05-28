# reco/generator.py
import json
import os
import pathlib
from typing import List

import openai

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

# Déport de la clé pour sécurité
_openai_api_key = os.getenv("OPENAI_API_KEY", "")


def _ensure_api_key():
    """
    Vérifie la présence de la clé API OpenAI.
    Lève RuntimeError si absente.
    """
    if not _openai_api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable")
    openai.api_key = _openai_api_key


def _call_llm(prompt_path: str, context: str) -> str:
    """
    Lit un fichier Markdown de prompt, injecte le contexte,
    appelle l'API OpenAI et retourne le texte brut.
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
    """
    Concatène le brief et les tendances en un contexte structuré pour le LLM.
    """
    lines = [f"# Brief\n{brief.summary}", "# Tendances"]
    for t in trends:
        lines.append(f"- {t.date} | {t.source} – {t.title}\n{t.snippet}")
    return "\n".join(lines)


def _parse_list(text: str) -> List[str]:
    """
    Extrait une liste à puces d'un texte brut issu du LLM.
    Gère les tirets, astérisques et numérotations.
    """
    return [
        line.lstrip("-*0123456789. ").strip()
        for line in text.splitlines()
        if line.strip()
    ]


# -- Générateurs par section --


def generate_insights(brief: BriefReminder, trends: List[TrendItem]) -> List[Idea]:
    raw = _call_llm("prompts/insights.md", _build_context(brief, trends))
    return [Idea(label=item) for item in _parse_list(raw)]


def generate_hypotheses(brief: BriefReminder, trends: List[TrendItem]) -> List[Idea]:
    raw = _call_llm("prompts/hypotheses.md", _build_context(brief, trends))
    return [Idea(label=item) for item in _parse_list(raw)]


def generate_kpis(brief: BriefReminder, trends: List[TrendItem]) -> List[Idea]:
    raw = _call_llm("prompts/kpis.md", _build_context(brief, trends))
    return [Idea(label=item) for item in _parse_list(raw)]


def generate_executive_summary(brief: BriefReminder, trends: List[TrendItem]) -> str:
    return _call_llm("prompts/executive_summary.md", _build_context(brief, trends))


def generate_ideas(brief: BriefReminder, trends: List[TrendItem]) -> List[Idea]:
    """
    Générateur d'idées : liste d'Idea, ou vide si pas de clé API.
    """
    try:
        raw = _call_llm("prompts/ideas.md", _build_context(brief, trends))
        return [Idea(label=line.strip()) for line in raw.splitlines() if line.strip()]
    except RuntimeError:
        return []


def generate_timeline(brief: BriefReminder, trends: List[TrendItem]) -> List[Milestone]:
    """
    Générateur de planning : liste de Milestone, ou vide si pas de clé API.
    """
    try:
        raw = _call_llm("prompts/timeline.md", _build_context(brief, trends))
    except RuntimeError:
        return []
    milestones: List[Milestone] = []
    for line in raw.splitlines():
        if ":" in line:
            date_part, label = line.split(":", 1)
            milestones.append(
                Milestone(deadline=date_part.strip(), label=label.strip())
            )
    return milestones


def generate_budget(brief: BriefReminder, trends: List[TrendItem]) -> List[BudgetItem]:
    """
    Générateur de budget : liste de BudgetItem, ou vide si pas de clé API.
    """
    try:
        raw = _call_llm("prompts/budget.md", _build_context(brief, trends))
    except RuntimeError:
        return []
    budget: List[BudgetItem] = []
    for line in raw.splitlines():
        parts = [p.strip() for p in line.split("–")]
        if len(parts) >= 2:
            try:
                amt = float(parts[1].replace("€", "").strip())
            except ValueError:
                continue
            comment = parts[2] if len(parts) > 2 else ""
            budget.append(BudgetItem(category=parts[0], estimate=amt, comment=comment))
    return budget


def generate_brand_overview(
    brief: BriefReminder, trends: List[TrendItem]
) -> BrandOverview:
    """
    Initialise la slide « Brand Overview » via LLM.
    Attendu : JSON parsable.
    """
    raw = _call_llm("prompts/brand_overview.md", _build_context(brief, trends))
    try:
        data = json.loads(raw)
        return BrandOverview(
            description_paragraphs=data["description_paragraphs"],
            competitive_positioning=data["competitive_positioning"],
            persona=data["persona"],
            top3_competitor_actions=data["top3_competitor_actions"],
        )
    except Exception:
        return BrandOverview(
            description_paragraphs=[],
            competitive_positioning={"axes": [], "brands": []},
            persona={"heading": [], "bullets": []},
            top3_competitor_actions=[],
        )


def generate_state_of_play(
    brief: BriefReminder, trends: List[TrendItem]
) -> List[StateOfPlaySection]:
    """
    Construit la section « State of Play » via LLM.
    Format attendu :
      Theme: <titre>
      - preuve
    """
    raw = _call_llm("prompts/state_of_play.md", _build_context(brief, trends))
    sections: List[StateOfPlaySection] = []
    current_theme = None
    current_evidence: List[str] = []
    for line in raw.splitlines():
        if line.lower().startswith("theme:"):
            if current_theme:
                sections.append(
                    StateOfPlaySection(theme=current_theme, evidence=current_evidence)
                )
            current_theme = line.split(":", 1)[1].strip()
            current_evidence = []
        elif line.lstrip().startswith(("-", "*")):
            current_evidence.append(line.lstrip("-* ").strip())
    if current_theme:
        sections.append(
            StateOfPlaySection(theme=current_theme, evidence=current_evidence)
        )
    return sections


def generate_recommendation(brief: BriefReminder, trends: List[TrendItem]) -> DeckData:
    """
    Orchestrateur principal : assemble un DeckData complet.
    """
    insights = generate_insights(brief, trends)
    hypotheses = generate_hypotheses(brief, trends)
    kpis = generate_kpis(brief, trends)
    executive_summary = generate_executive_summary(brief, trends)
    ideas = generate_ideas(brief, trends)
    timeline = generate_timeline(brief, trends)
    budget = generate_budget(brief, trends)
    brand_overview = generate_brand_overview(brief, trends)
    state_of_play = generate_state_of_play(brief, trends)

    return DeckData(
        brief_reminder=brief,
        brand_overview=brand_overview,
        state_of_play=state_of_play,
        insights=insights,
        hypotheses=hypotheses,
        kpis=kpis,
        executive_summary=executive_summary,
        ideas=ideas,
        timeline=timeline,
        budget=budget,
        trends=trends,
    )
