#!/usr/bin/env python3
import re
from typing import Dict, List


def extract_brief_sections(text: str) -> Dict[str, object]:
    """
    Extrait et reformule automatiquement les composantes clés d’un brief.
    Retourne un dict Pydantic-compatible :
    {
        "title": str,
        "objectives": List[str],
        "internal_reformulation": str,
        "summary": str
    }
    """
    # Normalisation des retours à la ligne
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Initialisation des sections
    sections = {
        "problem": "",
        "objectives": "",
        "KPIs": ""
    }

    # Détection des sections à partir de titres FR/EN
    title_pattern = r"(?:probl[eèé]me|problem|objectifs?|objectives|kpis?|indicateurs?)"
    section_re = re.compile(
        rf"(?P<title>^\s*{title_pattern}\s*:?)\s*(?P<body>.*?)(?=^\s*{title_pattern}\s*:?\s*|\Z)",
        flags=re.IGNORECASE | re.MULTILINE | re.DOTALL
    )

    for match in section_re.finditer(text):
        title = match.group("title").strip().lower().rstrip(":")
        body = match.group("body").strip()

        if "probl" in title or "problem" in title:
            sections["problem"] = body
        elif "object" in title:
            sections["objectives"] = body
        elif "kpi" in title or "indicateur" in title:
            sections["KPIs"] = body

    # Construction du dict final au format attendu
    parsed = {
        "title": "Brief extrait automatiquement",
        "objectives": _parse_list(sections["objectives"]),
        "internal_reformulation": f"Reformulation automatique du problème : {sections['problem'] or 'non précisé'}",
        "summary": f"Résumé automatique des KPIs : {sections['KPIs'] or 'non précisé'}"
    }

    # Fallback si les objectifs n’ont pas été extraits correctement
    if not parsed["objectives"]:
        parsed["objectives"] = ["Objectifs non identifiés (fallback automatique)"]

    return parsed


def _parse_list(text: str) -> List[str]:
    """
    Extrait une liste d’éléments à partir de texte brut formaté en puces.
    Gère les formes : - item, * item, 1. item, etc.
    """
    lines = text.strip().splitlines()
    return [
        re.sub(r"^[-*•\d.]+\s*", "", line).strip()
        for line in lines
        if line.strip()
    ]
