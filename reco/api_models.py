# reco/api_models.py
from typing import List, Optional
from pydantic import BaseModel
from datetime import date


class BriefReminder(BaseModel):
    title: str
    objectives: List[str]
    summary: str
    internal_reformulation: Optional[str] = ""


class TrendItem(BaseModel):
    source: str
    title: str
    date: date  # validation stricte ISO
    snippet: str
    theme: Optional[str] = ""
    evidence: List[str] = []


class RecommendationRequest(BaseModel):
    brief: BriefReminder
    trends: List[TrendItem]
