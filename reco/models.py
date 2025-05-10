from pydantic import BaseModel, Field
from typing import Optional

class BriefOutput(BaseModel):
    problem: str = Field(..., description="Définition du problème")
    objectives: str = Field(..., description="Objectifs à atteindre")
    KPIs: str = Field(..., description="Indicateurs clés")
    budget: Optional[str]
    deadline: Optional[str]
    audience: Optional[str]
    deliverables: Optional[str]
