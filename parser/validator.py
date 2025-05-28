import json
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft7Validator

from utils.logger import logger

_SCHEMAS: dict[str, dict[str, Any]] = {}


def _load_all_schemas(schema_dir: Path) -> None:
    for schema_file in schema_dir.glob("*.json"):
        try:
            raw_schema = json.loads(schema_file.read_text(encoding="utf-8"))
            Draft7Validator.check_schema(raw_schema)
            base_name = schema_file.stem
            _SCHEMAS[base_name] = raw_schema
            cleaned = (
                base_name.replace(".schema", "")
                .replace("_schema", "")
                .replace("-schema", "")
            )
            _SCHEMAS[cleaned] = raw_schema
            logger.debug(
                f"[validator] Schéma chargé : {schema_file.name} "
                f"→ clés : {base_name}, {cleaned}"
            )
        except json.JSONDecodeError:
            logger.warning(
                f"[validator] Fichier JSON invalide ignoré : {schema_file.name}"
            )
        except jsonschema.exceptions.SchemaError as e:
            logger.warning(
                f"[validator] Schéma JSON invalide : {schema_file.name} → {e}"
            )
        except Exception as e:
            logger.error(
                f"[validator] Échec de chargement pour {schema_file.name} → {e}"
            )

_CORRECT_SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schema"
_load_all_schemas(_CORRECT_SCHEMA_DIR)


def validate(instance: dict[str, Any], schema_name: str) -> None:
    schema = _SCHEMAS.get(schema_name)
    if not schema:
        logger.error(
            f"[validator] Tentative de validation avec schéma inconnu: '{schema_name}'. "
            f"Schémas disponibles: {list(_SCHEMAS.keys())}"
        )
        raise ValueError(f"Unknown schema: {schema_name}")

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)

    if errors:
        error_messages = [
            f"{'.'.join(str(p) for p in error.path) or '<root>'}: {error.message}"
            for error in errors
        ]
        detail = "; ".join(error_messages)
        logger.error(f"[validator] Validation échouée pour '{schema_name}': {detail}")
        raise jsonschema.ValidationError(
            f"Validation failed for '{schema_name}': {detail}"
        )