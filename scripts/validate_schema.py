#!/usr/bin/env python3
import json
import os

from jsonschema import ValidationError, validate

DATA_DIR = "data"
SCHEMA_PATH = "schema/brief_schema.json"


def load_schema(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate_json_file(file_path: str, schema: dict) -> bool:
    with open(file_path, encoding="utf-8") as f:
        try:
            data = json.load(f)
            validate(instance=data, schema=schema)
            print(f"✅ {file_path} : OK")
            return True
        except ValidationError as e:
            print(f"❌ {file_path} : ValidationError → {e.message}")
        except json.JSONDecodeError as e:
            print(f"❌ {file_path} : JSONDecodeError → {e}")
    return False


def main():
    if not os.path.exists(SCHEMA_PATH):
        print(f"❌ Schéma introuvable : {SCHEMA_PATH}")
        exit(1)

    schema = load_schema(SCHEMA_PATH)
    json_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]

    if not json_files:
        print("⚠️  Aucun fichier .json trouvé dans data/")
        return

    all_passed = True
    for filename in json_files:
        path = os.path.join(DATA_DIR, filename)
        if not validate_json_file(path, schema):
            all_passed = False

    if not all_passed:
        exit(1)


if __name__ == "__main__":
    main()
