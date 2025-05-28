import re
from typing import Dict, List


def extract_brief_sections(text: str) -> Dict[str, object]:
    """
    Extrait les sections clés d’un brief à partir d’un texte brut de PDF.

    Retourne un dictionnaire conforme au schéma français (brief_schema.json) :
      - titre: str
      - problème: str
      - objectifs: str
      - kpis: List[str]
    """
    # Normaliser les sauts de ligne
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Pattern des en-têtes de sections
    section_titles = r"(?:titre|probl[eèé]me|objectifs?|kpis?|indicateurs?)"
    section_re = re.compile(
        rf"^\s*(?P<title>{section_titles})\s*:?\s*(?P<body>.*?)(?=^\s*{section_titles}\s*:?\s*|\Z)",
        flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )

    raw = {"titre": "", "problème": "", "objectifs": "", "kpis": ""}

    for m in section_re.finditer(text):
        key = m.group("title").strip().lower()
        body = m.group("body").strip()
        if key.startswith("tit"):
            raw["titre"] = body
        elif "probl" in key:
            raw["problème"] = body
        elif "object" in key:
            raw["objectifs"] = body
        elif "kpi" in key or "indicateur" in key:
            raw["kpis"] = body

    def parse_list(txt: str) -> List[str]:
        lines = txt.strip().splitlines()
        items = []
        for l in lines:
            # enlever puces, chiffres, etc.
            item = re.sub(r"^[-*•\d.]+\s*", "", l).strip()
            if item:
                items.append(item)
        return items

    # Valeurs finales avec fallback
    titre = raw["titre"] or "Brief extrait automatiquement"
    probleme = raw["problème"] or "Problème non précisé"

    if raw["objectifs"]:
        objectifs = "; ".join(parse_list(raw["objectifs"]))
    else:
        objectifs = "Objectifs non précisés"

    kpis_list = parse_list(raw["kpis"]) or ["KPI non identifié"]

    return {
        "titre": titre,
        "problème": probleme,
        "objectifs": objectifs,
        "kpis": kpis_list,
    }
