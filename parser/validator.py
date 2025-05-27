"""
Validation logic for JSON data against schemas in /schemas directory.
"""

import json
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft7Validator

from utils.logger import logger

# Conteneur global pour tous les schémas chargés
_SCHEMAS: dict[str, dict[str, Any]] = {}


def _load_all_schemas(schema_dir: Path) -> None:
    """
    Charge tous les fichiers .json valides depuis `schema_dir` et enregistre les schémas
    sous plusieurs clés : nom brut, sans suffixes (_schema, .schema), etc.
    """
    for schema_file in schema_dir.glob("*.json"):
        try:
            raw_schema = json.loads(schema_file.read_text(encoding="utf-8"))
            Draft7Validator.check_schema(raw_schema)

            # Nom du fichier sans extension
            base_name = schema_file.stem  # ex: "brief_output.schema"
            _SCHEMAS[base_name] = raw_schema

            # Ajoute des clés alternatives sans suffixe
            cleaned = (
                base_name.replace(".schema", "")
                .replace("_schema", "")
                .replace("-schema", "")
            )
            _SCHEMAS[cleaned] = raw_schema

            logger.debug(
                f"[validator] Schéma chargé : {schema_file.name} → clés : {base_name}, {cleaned}"
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


# Chargement automatique à l'import
_load_all_schemas(Path(__file__).resolve().parent.parent / "schemas")


def validate(instance: dict[str, Any], schema_name: str) -> None:
    """
    Valide un objet Python contre un schéma JSON identifié par son nom.

    Args:
        instance: Dictionnaire à valider.
        schema_name: Nom du schéma (ex: "brief_output").

    Raises:
        ValueError: Si le nom du schéma est inconnu.
        jsonschema.ValidationError: Si la validation échoue.
    """
    schema = _SCHEMAS.get(schema_name)
    if not schema:
        raise ValueError(f"Unknown schema: {schema_name}")

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)

    if errors:
        error_messages = [
            f"{'.'.join(str(p) for p in error.path) or '<root>'}: {error.message}"
            for error in errors
        ]
        detail = "; ".join(error_messages)
        logger.error(f"[validator] Validation échouée pour '{schema_name}' : {detail}")
        raise jsonschema.ValidationError(
            f"Validation failed for '{schema_name}': {detail}"
        )
