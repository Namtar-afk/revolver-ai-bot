from pydantic import BaseModel
from typing import List, Optional

class Action(BaseModel):
    title: str
    desc: str

class CompetitorActions(BaseModel):
    competitor: str
    actions: List[Action]

class BriefReminder(BaseModel):
    objectives: List[str]
    internal_reformulation: str

class BrandOverview(BaseModel):
    description_paragraphs: List[str]
    competitive_positioning: dict  # voir TrendItem pour grille
    persona: dict
    top3_competitor_actions: List[CompetitorActions]

class StateOfPlaySection(BaseModel):
    theme: str
    evidence: List[Action]

class DeckData(BaseModel):
    brief_reminder: BriefReminder
    brand_overview: BrandOverview
    state_of_play: List[StateOfPlaySection]
    # … plus tard : ideas, timeline, budget
