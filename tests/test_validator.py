import jsonschema
import pytest

# Assure-toi que cet import pointe vers ta fonction de validation actuelle
from parser.validator import validate 

# Instance valide avec des clés françaises, correspondant à ce que 
# 'brief_output.schema.json' (version française) devrait attendre.
VALID_INSTANCE_FR = {
    "titre": "Un Titre Valide en Français",
    "objectifs": ["Objectif A en français", "Objectif B en français"], # Supposant que le schéma attend une liste de chaînes
    "reformulation_interne": "Ceci est une reformulation interne.",
    "résumé": "Ceci est un résumé succinct.",
    # Optionnel: ajoute d'autres champs si ton schéma brief_output les définit (ex: problème, kpis)
    # "problème": "Description du problème si inclus dans brief_output.",
    # "kpis": ["KPI un", "KPI deux"] 
}

# Instance invalide où un champ requis français (ex: "résumé") est manquant.
INVALID_INSTANCE_MISSING_FR = {
    "titre": "Titre de test pour champ manquant",
    "objectifs": ["Objectif unique"],
    "reformulation_interne": "Reformulation pour test.",
    # Le champ "résumé" est volontairement omis
}

# Instance invalide basée sur VALID_INSTANCE_FR avec une propriété additionnelle non autorisée.
INVALID_INSTANCE_EXTRA_FR = {
    **VALID_INSTANCE_FR, # Déstructure l'instance valide
    "propriete_additionnelle_interdite": 12345 
}


def test_validate_success():
    """
    Teste qu'une instance valide (clés françaises) passe la validation
    contre le schéma 'brief_output' (supposé français).
    """
    # Ne devrait pas lever d'exception si VALID_INSTANCE_FR est conforme
    # au schéma français 'brief_output.schema.json'
    try:
        validate(VALID_INSTANCE_FR, "brief_output")
    except jsonschema.ValidationError as e:
        pytest.fail(
            "La validation de VALID_INSTANCE_FR a échoué de manière inattendue "
            f"contre le schéma 'brief_output'. Assurez-vous que "
            f"'schema/brief_output.schema.json' est en français et correspond à VALID_INSTANCE_FR.\nErreur: {e}"
        )


def test_validate_unknown_schema():
    """
    Teste que la validation échoue avec ValueError si le nom du schéma est inconnu.
    """
    with pytest.raises(ValueError) as exc_info:
        validate(VALID_INSTANCE_FR, "schema_inexistant_ou_mal_nomme")
    assert "Unknown schema" in str(exc_info.value)


def test_validate_missing_required_french_field():
    """
    Teste que la validation échoue si un champ requis français est manquant.
    Ici, 'résumé' est manquant dans INVALID_INSTANCE_MISSING_FR.
    """
    with pytest.raises(jsonschema.ValidationError) as exc_info:
        validate(INVALID_INSTANCE_MISSING_FR, "brief_output")
    
    error_message = str(exc_info.value).lower() # Comparaison insensible à la casse pour plus de robustesse
    # Le message d'erreur devrait mentionner le champ manquant 'résumé'.
    assert "'résumé' is a required property" in error_message or \
           "champ obligatoire manquant : résumé" in error_message, \
           f"L'erreur de validation ne mentionne pas 'résumé' comme manquant. Message: {exc_info.value}"


def test_validate_additional_french_property():
    """
    Teste que la validation échoue si une propriété additionnelle non définie
    est présente et que additionalProperties=false dans le schéma français.
    """
    with pytest.raises(jsonschema.ValidationError) as exc_info:
        validate(INVALID_INSTANCE_EXTRA_FR, "brief_output")
    
    error_message = str(exc_info.value).lower()
    # Le message d'erreur devrait indiquer un problème avec les propriétés additionnelles.
    assert "additional properties are not allowed" in error_message or \
           "propriétés additionnelles ne sont pas autorisées" in error_message or \
           "'propriete_additionnelle_interdite' was unexpected" in error_message, \
           f"L'erreur de validation n'indique pas correctement le problème de propriété additionnelle. Message: {exc_info.value}"