from typing import List, Dict, Any
from pydantic import BaseModel

class BrandPosition(BaseModel):
    name: str
    x: float
    y: float

class Action(BaseModel):
    title: str
    desc: str

class CompetitorActions(BaseModel):
    competitor: str
    actions: List[Action]

class BriefReminder(BaseModel):
    title: str
    objectives: List[str]
    internal_reformulation: str

class BrandOverview(BaseModel):
    description_paragraphs: List[str]
    competitive_positioning: Dict[str, Any]
    persona: Dict[str, Any]
    top3_competitor_actions: List[CompetitorActions]

class StateOfPlaySection(BaseModel):
    theme: str
    evidence: List[Action]

class Idea(BaseModel):
    title: str
    body: str

class Milestone(BaseModel):
    milestone: str
    date: str

class BudgetItem(BaseModel):
    item: str
    amount: float

class DeckData(BaseModel):
    brief_reminder: BriefReminder
    brand_overview: BrandOverview
    state_of_play: List[StateOfPlaySection]
    ideas: List[Idea]
    timeline: List[Milestone]
    budget: List[BudgetItem]
