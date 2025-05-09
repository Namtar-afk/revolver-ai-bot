import re
import spacy
from typing import Dict

nlp = spacy.load("fr_core_news_md")

def extract_brief_sections(text: str) -> Dict[str, str]:
    sections = {
        "problem": "",
        "objectives": "",
        "KPIs": ""
    }

    # Regex primaire avec délimitation par titres ou fin de bloc
    patterns = {
        "problem": r"(?i)probl[eè]me(?:[^\n]*)\n(.*?)(?=\n[A-Z]|Objectifs?|KPIs?)",
        "objectives": r"(?i)objectifs?(?:[^\n]*)\n(.*?)(?=\n[A-Z]|KPIs?)",
        "KPIs": r"(?i)(?:KPIs?|indicateurs?)(?:[^\n]*)\n(.*?)(?=\n[A-Z]|$)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL)
        if match:
            sections[key] = match.group(1).strip()

    # Fallback via spaCy NLP si une section est vide
    if any(not v.strip() for v in sections.values()):
        doc = nlp(text)
        current = None
        temp = {"problem": "", "objectives": "", "KPIs": ""}
        for sent in doc.sents:
            s = sent.text.strip()
            lowered = s.lower()
            if "problème" in lowered:
                current = "problem"
            elif "objectif" in lowered:
                current = "objectives"
            elif "kpi" in lowered or "indicateur" in lowered:
                current = "KPIs"
            elif current:
                temp[current] += s + "\n"

        for k in sections:
            if not sections[k].strip() and temp[k].strip():
                sections[k] = temp[k].strip()

    return sections

