# reco/models.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class BriefReminder:
    """
    Résumé du brief client servant de base à la recommandation stratégique.
    """

    title: str  # Titre du projet ou de la mission
    objectives: List[str]  # Liste des objectifs attendus par le client
    summary: str  # Résumé synthétique utilisé pour le prompt LLM
    internal_reformulation: Optional[str] = ""  # Reformulation stratégique par l'équipe


@dataclass(frozen=True)
class TrendItem:
    """
    Élément de tendance détecté dans les sources de veille.
    """

    source: str  # Ex: "TikTok", "Instagram", "Nielsen"
    title: str  # Titre ou accroche de la tendance
    date: str  # Date de publication ou d'observation (format ISO recommandé)
    snippet: str  # Extrait ou résumé de la tendance
    theme: Optional[str] = ""  # Thème regroupant cette tendance
    evidence: List[str] = field(
        default_factory=list
    )  # Preuves, citations ou sources associées


@dataclass(frozen=True)
class StateOfPlaySection:
    """
    Section synthétique décrivant un thème d’actualité à partir de plusieurs preuves.
    """

    theme: str  # Nom du thème (ex: "Renaissance fongique")
    evidence: List[str]  # Exemples, citations, données soutenant ce thème


@dataclass(frozen=True)
class Idea:
    """
    Élément structurant de la recommandation : idée, KPI ou hypothèse.
    """

    label: str  # Intitulé de l'idée ou de l'item
    bullets: List[str] = field(default_factory=list)  # Détails ou sous-points associés


@dataclass(frozen=True)
class BrandOverview:
    """
    Revue d'ensemble de la marque cliente et de son contexte concurrentiel.
    """

    description_paragraphs: List[str]  # Paragraphes de présentation de la marque
    competitive_positioning: Dict[str, List[str]]  # {"axes": [...], "brands": [...]}
    persona: Dict[str, List[str]]  # {"heading": [...], "bullets": [...]}
    top3_competitor_actions: List[str]  # Actions clés repérées chez la concurrence


@dataclass(frozen=True)
class Milestone:
    """
    Étape clé du projet avec date de livraison prévue.
    """

    label: str  # Nom de l'étape (ex: "Kick-off", "Campagne live")
    deadline: str  # Date attendue ou cible (ISO format recommandé)


@dataclass(frozen=True)
class BudgetItem:
    """
    Ligne budgétaire estimée pour le projet.
    """

    category: str  # Catégorie budgétaire (ex: "Production vidéo")
    estimate: float  # Montant estimé (en euros)
    comment: Optional[str] = ""  # Note ou explication sur cette ligne


@dataclass(frozen=True)
class DeckData:
    """
    Structure complète d'une recommandation prête à être transformée en slides.
    """

    brief_reminder: BriefReminder
    brand_overview: BrandOverview
    state_of_play: List[StateOfPlaySection]
    insights: List[Idea]
    hypotheses: List[Idea]
    kpis: List[Idea]
    executive_summary: str  # Synthèse exécutive pour introduction / slide dédiée
    ideas: List[Idea]
    timeline: List[Milestone]
    budget: List[BudgetItem]
    trends: List[TrendItem] = field(
        default_factory=list
    )  # Contexte de tendances pour enrichir les sections
