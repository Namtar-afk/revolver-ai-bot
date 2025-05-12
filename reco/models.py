from typing import List, Dict, Optional
from pydantic import BaseModel


# === Brief ===

class BriefReminder(BaseModel):
    """
    Résumé du brief client servant de base à la recommandation stratégique.
    """
    title: str  # Titre du projet ou de la mission
    objectives: List[str]  # Liste des objectifs attendus par le client
    internal_reformulation: Optional[str] = ""  # Reformulation stratégique par l'équipe
    summary: str  # Résumé synthétique utilisé pour le prompt LLM


# === Tendances & État des lieux ===

class TrendItem(BaseModel):
    """
    Élément de tendance détecté dans les sources de veille.
    """
    source: str  # Ex: "TikTok", "Instagram", "Nielsen"
    title: str  # Titre ou accroche de la tendance
    date: str  # Date de publication ou d'observation
    snippet: str  # Extrait ou résumé de la tendance
    theme: str  # Thème regroupant cette tendance (ex: "Naturalité")
    evidence: List[str]  # Preuves, citations ou sources associées


class StateOfPlaySection(BaseModel):
    """
    Section synthétique décrivant un thème d’actualité à partir de plusieurs preuves.
    """
    theme: str  # Nom du thème (ex: "Renaissance fongique")
    evidence: List[str]  # Exemples, citations, données soutenant ce thème


# === Idées, KPIs, Hypothèses ===

class Idea(BaseModel):
    """
    Élément structurant de la recommandation : idée, KPI ou hypothèse.
    """
    label: str  # Intitulé de l'idée ou de l'item
    bullets: List[str]  # Détails ou sous-points associés (optionnel)


# === Brand Overview ===

class BrandOverview(BaseModel):
    """
    Revue d'ensemble de la marque cliente et de son contexte concurrentiel.
    """
    description_paragraphs: List[str]  # Paragraphes de présentation de la marque
    competitive_positioning: Dict[str, List[str]]  # {"axes": [...], "brands": [...]}
    persona: Dict[str, List[str]]  # {"heading": [...], "bullets": [...]}
    top3_competitor_actions: List[str]  # Actions clés repérées chez la concurrence


# === Planning & Budget ===

class Milestone(BaseModel):
    """
    Étape clé du projet avec date de livraison prévue.
    """
    label: str  # Nom de l'étape (ex: "Kick-off", "Campagne live")
    deadline: str  # Date attendue ou cible


class BudgetItem(BaseModel):
    """
    Ligne budgétaire estimée pour le projet.
    """
    category: str  # Catégorie budgétaire (ex: "Production vidéo")
    estimate: float  # Montant estimé (en euros)
    comment: str  # Note ou explication sur cette ligne


# === Output global du deck final ===

class DeckData(BaseModel):
    """
    Structure complète d'une recommandation prête à être transformée en slides.
    """
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