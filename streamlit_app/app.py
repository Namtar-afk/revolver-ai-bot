from parser.nlp_utils import extract_brief_sections
from parser.pdf_parser import extract_text_from_pdf

import streamlit as st

st.set_page_config(page_title="Extraction de Brief", layout="centered")
st.title("🧠 Extraction de Brief Automatisée")

uploaded_file = st.file_uploader("📎 Déposez un fichier PDF de brief", type=["pdf"])

if uploaded_file:
    with open("temp_brief.pdf", "wb") as f:
        f.write(uploaded_file.read())

    st.info("📤 Fichier reçu. Analyse en cours...")
    text = extract_text_from_pdf("temp_brief.pdf")

    if text:
        try:
            brief_data = extract_brief_sections(text)
            st.success("✅ Extraction réussie !")
            st.json(brief_data)
        except Exception as e:
            st.error(f"❌ Erreur lors de l'extraction : {e}")
    else:
        st.error("❌ Impossible de lire le contenu du PDF.")
