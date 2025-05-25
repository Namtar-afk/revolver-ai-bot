import json
from pathlib import Path

import jsonschema
from jsonschema import Draft7Validator

from utils.logger import logger

# Charge et enregistre tous les schémas JSON valides depuis schema/ à la racine
_SCHEMAS: dict[str, dict] = {}
schema_dir = Path(__file__).parent.parent / "schema"
for schema_file in schema_dir.glob("*.json"):
    name = schema_file.stem  # ex. "brief_schema"
    try:
        raw = json.loads(schema_file.read_text(encoding="utf-8"))
        # Vérifie que le schéma lui-même est valide
        Draft7Validator.check_schema(raw)
        # Enregistre sous le nom de base
        _SCHEMAS[name] = raw
        # Ajoute aussi des clés normalisées (avec/sans suffixes)
        if name.endswith(".schema"):
            _SCHEMAS[name[:-7]] = raw
        if name.endswith("_schema"):
            _SCHEMAS[name[:-7]] = raw
    except json.JSONDecodeError:
        logger.warning(f"[validator] Skipping invalid JSON file: {schema_file.name}")
    except jsonschema.exceptions.SchemaError as e:
        logger.warning(f"[validator] Invalid JSON schema {schema_file.name}: {e}")
    except Exception as e:
        logger.error(f"[validator] Failed to load schema {schema_file.name}: {e}")


def validate(instance: dict, schema_name: str) -> None:
    """
    Valide un objet dict contre le schéma nommé.
    Lève jsonschema.ValidationError sur échec,
    ValueError si le nom de schéma est inconnu.
    """
    schema = _SCHEMAS.get(schema_name)
    if schema is None:
        raise ValueError(f"Unknown schema: {schema_name}")

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    if errors:
        messages = []
        for err in errors:
            path = ".".join(str(p) for p in err.path) or "<root>"
            messages.append(f"{path}: {err.message}")
        detail = "; ".join(messages)
        logger.error(f"[validator] Validation failed for {schema_name}: {detail}")
        raise jsonschema.ValidationError(f"Validation {schema_name} failure: {detail}")