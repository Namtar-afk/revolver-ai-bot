# parser/pdf_parser.py
import json
import re
from pathlib import Path
from typing import Optional

import pdfplumber
from utils.logger import logger # Assure-toi que ce chemin d'import est correct


def _clean_semantic(text: str) -> str:
    """
    Perform line-level semantic cleaning:
    - Merge hyphenated words at line breaks
    - Collapse multiple spaces
    - Remove empty lines
    - Normalize quotes and dashes
    """
    text = text.replace("“", '"').replace("”", '"').replace("’", "'")
    text = text.replace("–", "-").replace("—", "-")

    lines = text.splitlines()
    cleaned_lines = []
    buffer = ""
    for line in lines:
        line = line.rstrip()
        if not line:
            continue
        if buffer:
            if buffer.endswith("-"):
                buffer = buffer[:-1] + line.lstrip()
            else:
                cleaned_lines.append(buffer)
                buffer = line
        else:
            buffer = line
    if buffer:
        cleaned_lines.append(buffer)

    cleaned_lines = [re.sub(r"\s{2,}", " ", l) for l in cleaned_lines]
    return "\n".join(cleaned_lines)


def extract_text_from_pdf(file_path: str) -> Optional[str]:
    path = Path(file_path)
    if not path.exists():
        logger.error(f"[pdf_parser] Fichier non trouvé : {file_path}")
        return None
    try:
        with pdfplumber.open(path) as pdf:
            pages = []
            for page in pdf.pages:
                raw_text = page.extract_text() # Renommé `raw` en `raw_text` pour clarté
                if raw_text and raw_text.strip():
                    pages.append(_clean_semantic(raw_text))
            if not pages:
                logger.warning(f"[pdf_parser] Aucun texte substantiel n'a été extrait du PDF: {file_path}")
                return None # Retourner None si aucune page n'a de contenu extractible
            return "\n".join(pages)
    except Exception as e:
        logger.error(f"[pdf_parser] Erreur lors de l'extraction du texte du PDF: {file_path} ({e})")
        return None


def extract_json_from_text(text: str) -> Optional[dict]:
    """
    Parses the first valid JSON object found in the text, normalizes its keys to French,
    converts specific fields (like 'objectifs', 'kpis') to list if necessary,
    and validates it against the 'brief_output' schema.
    """
    if not text or not text.strip():
        logger.warning("[pdf_parser] Tentative d'extraction de JSON depuis un texte vide ou ne contenant que des espaces.")
        return None

    json_str_for_error_reporting = "" # Pour un meilleur contexte en cas de JSONDecodeError

    try:
        start_index = text.find("{")
        if start_index == -1:
            logger.warning("[pdf_parser] Aucune accolade ouvrante '{' trouvée dans le texte.")
            # Ne pas lever d'erreur ici, laisser le test vérifier si None est retourné
            return None # Retourne None si aucune accolade ouvrante n'est trouvée

        # Essayer de trouver l'accolade fermante correspondante
        brace_level = 0
        end_index = -1
        for i in range(start_index, len(text)):
            if text[i] == '{':
                brace_level += 1
            elif text[i] == '}':
                brace_level -= 1
                if brace_level == 0:
                    end_index = i + 1 # Inclure l'accolade fermante
                    break
        
        if end_index == -1:
            logger.warning(f"[pdf_parser] Accolade ouvrante '{{' trouvée à l'index {start_index}, mais pas d'accolade fermante '}}' correspondante.")
            return None # Retourne None si pas d'accolade fermante correspondante
            
        json_str = text[start_index:end_index]
        json_str_for_error_reporting = json_str 
        
        data = json.loads(json_str)
        
        # Clés anglaises potentielles dans le JSON du PDF et leurs équivalents français
        # pour le schéma 'brief_output'.
        key_map_en_to_fr = {
            "title": "titre",
            "problem": "problème",
            "objectives": "objectifs",
            "kpis": "kpis",
            "internal_reformulation": "reformulation_interne",
            "summary": "résumé",
            # Ajoute d'autres mappings si tes PDF peuvent contenir d'autres clés anglaises pertinentes
        }
        
        normalized_data = {}
        if isinstance(data, dict): 
            for original_key, value in data.items():
                # Normaliser la clé originale (ex: 'Title', 'title') en minuscule pour le mapping
                mapped_fr_key = key_map_en_to_fr.get(original_key.lower(), original_key)
                
                # Conversion de type pour 'objectifs' et 'kpis' si ce sont des chaînes
                # (le schéma 'brief_output.schema.json' attend des listes de chaînes pour eux)
                if mapped_fr_key == "objectifs":
                    if isinstance(value, str) and value.strip():
                        normalized_data[mapped_fr_key] = [obj.strip() for obj in value.split(';') if obj.strip()]
                    elif isinstance(value, list):
                         normalized_data[mapped_fr_key] = [str(item).strip() for item in value if str(item).strip()]
                    else:
                        normalized_data[mapped_fr_key] = [] # Défaut à une liste vide
                elif mapped_fr_key == "kpis":
                    if isinstance(value, str) and value.strip():
                        normalized_data[mapped_fr_key] = [kpi.strip() for kpi in value.split(';') if kpi.strip()]
                    elif isinstance(value, list):
                        normalized_data[mapped_fr_key] = [str(item).strip() for item in value if str(item).strip()]
                    else:
                        normalized_data[mapped_fr_key] = [] # Défaut à une liste vide
                else:
                    normalized_data[mapped_fr_key] = value
            data_to_validate = normalized_data
        else:
            logger.warning(f"[pdf_parser] Le JSON extrait n'est pas un objet/dictionnaire attendu: {type(data)}")
            return None 
        
        # Validation contre le schéma 'brief_output' (qui est français)
        from parser.validator import validate as _validate 
        _validate(data_to_validate, "brief_output") 
        
        logger.info("[pdf_parser] JSON extrait, normalisé et validé avec succès.")
        return data_to_validate

    except json.JSONDecodeError as jde:
        error_context_start = max(0, jde.pos - 30)
        error_context_end = min(len(json_str_for_error_reporting), jde.pos + 30)
        context_snippet = json_str_for_error_reporting[error_context_start:error_context_end]
        logger.error(f"[pdf_parser] Échec du parsing JSON (JSONDecodeError): {jde}. Contexte: ...'{context_snippet}'... dans la chaîne parsée: '{json_str_for_error_reporting[:200]}...'")
        return None
    except ValueError as ve: # Capturer les ValueErrors levées par nous (ex: "No JSON...")
        logger.error(f"[pdf_parser] Erreur de valeur lors de l'extraction JSON: {ve}")
        return None
    except Exception as e: # Inclut jsonschema.ValidationError de _validate ou autres erreurs inattendues
        logger.error(f"[pdf_parser] Échec général de l'extraction/validation JSON: {e} (type: {type(e)})")
        return None