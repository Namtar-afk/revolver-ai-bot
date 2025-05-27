# reco/models.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class BriefReminder:
    title: str
    objectives: List[str]
    summary: str
    internal_reformulation: Optional[str] = ""


@dataclass(frozen=True)
class TrendItem:
    source: str
    title: str
    date: str
    snippet: str
    theme: Optional[str] = ""
    evidence: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class StateOfPlaySection:
    theme: str
    evidence: List[str]


@dataclass(frozen=True)
class Idea:
    label: str
    bullets: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class BrandOverview:
    description_paragraphs: List[str]
    competitive_positioning: Dict[str, List[str]]
    persona: Dict[str, List[str]]
    top3_competitor_actions: List[str]


@dataclass(frozen=True)
class Milestone:
    label: str
    deadline: str


@dataclass(frozen=True)
class BudgetItem:
    category: str
    estimate: float
    comment: Optional[str] = ""


@dataclass(frozen=True)
class DeckData:
    brief_reminder: BriefReminder
    brand_overview: BrandOverview
    state_of_play: List[StateOfPlaySection]
    insights: List[Idea]
    hypotheses: List[Idea]
    kpis: List[Idea]
    executive_summary: str
    ideas: List[Idea]
    timeline: List[Milestone]
    budget: List[BudgetItem]
    trends: List[TrendItem] = field(default_factory=list)
