import streamlit as st
from parser.pdf_parser import extract_text_from_pdf
from parser.nlp_utils import extract_brief_sections

st.title("Revolver AI Bot")
pdf_file = st.file_uploader("Upload brief PDF", type="pdf")
if pdf_file:
    text = extract_text_from_pdf(pdf_file)
    sections = extract_brief_sections(text)
    st.json(sections)
