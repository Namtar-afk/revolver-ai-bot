#!/usr/bin/env python3
import re
from typing import Dict, List

def extract_brief_sections(text: str) -> Dict[str, object]:
    """
    Extrait automatiquement :
      - title (libellé générique)
      - objectives (liste)
      - internal_reformulation (du ‘problème’)
      - summary (des KPIs)
    """

    # Normalisation
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # On cherche problem, objectifs et KPIs en FR/EN
    title_re = r"(?:probl[eèé]me|problem|objectifs?|objectives|kpis?|indicateurs?)"
    pattern = re.compile(
        rf"(?P<header>^\s*{title_re}\s*:?)\s*"
        rf"(?P<body>.*?)(?=^\s*{title_re}\s*:?\s*|\Z)",
        flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )

    raw = {"problem": "", "objectives": [], "KPIs": ""}
    for m in pattern.finditer(text):
        h = m.group("header").strip().lower()
        body = m.group("body").strip()
        if re.search(r"probl", h):
            raw["problem"] = body
        elif re.search(r"object", h):
            # liste à puces ou séparateurs « - » / « * »
            items = [l.strip(" -*•") for l in body.splitlines() if l.strip()]
            raw["objectives"] = items or [body]
        else:
            raw["KPIs"] = body

    # Fallback minimal
    title = "Brief extrait automatiquement"
    objectives = raw["objectives"] or ["Objectif non précisé"]
    internal_reformulation = (
        f"Reformulation automatique du problème : {raw['problem']}"
        if raw["problem"] else "Reformulation automatique du problème non précisé"
    )
    summary = (
        f"Résumé automatique des KPIs : {raw['KPIs']}"
        if raw["KPIs"] else "Résumé automatique des KPIs non précisé"
    )

    return {
        "title": title,
        "objectives": objectives,
        "internal_reformulation": internal_reformulation,
        "summary": summary
    }
