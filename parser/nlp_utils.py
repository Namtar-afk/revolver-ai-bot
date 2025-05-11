#!/usr/bin/env python3
import re
from typing import Dict

def extract_brief_sections(text: str) -> Dict[str, str]:
    """
    Extrait 'problem', 'objectives' et 'KPIs' d'un texte brut,
    détecte les titres FR/EN (avec ou sans deux-points) et capture
    tout le bloc jusqu'au titre suivant.
    """
    sections = {"problem": "", "objectives": "", "KPIs": ""}
    # Normalisation des retours chariot
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # On autorise un deux-points optionnel après le titre
    title_re = r"(?:probl[eèé]me|problem|objectifs?|objectives|kpis?|indicateurs?)"
    pattern = re.compile(
        rf"(?P<title>^\s*{title_re}\s*:?)\s*"
        rf"(?P<body>.*?)(?=^\s*{title_re}\s*:?\s*|\Z)",
        flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )

    for m in pattern.finditer(text):
        title = m.group("title").strip().lower().rstrip(':')
        body = m.group("body").strip().replace("\n", " ")
        if "probl" in title:
            sections["problem"] = body
        elif "object" in title:
            sections["objectives"] = body
        else:
            sections["KPIs"] = body

    # If any section is still empty, fill with a default placeholder
    for k, v in sections.items():
        if len(v) < 5:
            sections[k] = "Non précisé"

    return sections
