import os
from bot.orchestrator import process_brief

def simulate_slack_upload():
    sample_path = "tests/samples/brief_sample.pdf"
    if not os.path.exists(sample_path):
        print(f"❌ Fichier manquant : {sample_path}")
        return

    try:
        result = process_brief(sample_path)
        print("\n🧠 Résultat structuré du brief :")
        for k, v in result.items():
            print(f"\n== {k.upper()} ==\n{v}")
    except Exception as e:
        print(f"❌ Erreur dans le traitement du brief : {e}")

