#!/usr/bin/env python3
import re
from typing import Dict, List


def extract_brief_sections(text: str) -> Dict[str, object]:
    """
    Extrait les sections principales du brief (problème, objectifs, KPIs)
    et les reformule dans un format compatible avec BriefReminder.
    """
    sections = {"problem": "", "objectives": "", "KPIs": ""}
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Titre de section possible (fr/en) avec deux-points optionnel
    title_re = r"(?:probl[eèé]me|problem|objectifs?|objectives|kpis?|indicateurs?)"
    pattern = re.compile(
        rf"(?P<title>^\s*{title_re}\s*:?)\s*"
        rf"(?P<body>.*?)(?=^\s*{title_re}\s*:?\s*|\Z)",
        flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )

    for m in pattern.finditer(text):
        title = m.group("title").strip().lower().rstrip(":")
        body = m.group("body").strip().replace("\n", " ")
        if "probl" in title:
            sections["problem"] = body
        elif "object" in title:
            sections["objectives"] = body
        else:
            sections["KPIs"] = body

    # Séparation des objectifs en liste
    raw_objectives = sections["objectives"]
    objectives = [s.strip() for s in re.split(r"[\n•;\-–]", raw_objectives) if len(s.strip()) > 2]
    if not objectives:
        objectives = [raw_objectives.strip()] if raw_objectives.strip() else ["Objectif générique"]

    # Formattage final conforme au modèle BriefReminder
    return {
        "title": "Brief extrait automatiquement",
        "objectives": objectives,
        "internal_reformulation": f"Reformulation automatique du problème : {sections['problem']}",
        "summary": f"Résumé automatique des KPIs : {sections['KPIs']}"
    }
