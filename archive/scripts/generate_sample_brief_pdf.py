#!/usr/bin/env python3
from fpdf import FPDF
import os

BRIEF_MD = """
Problème : Le marché des soins naturels est saturé.

Objectifs :
- Accroître la notoriété de la marque
- Générer de l'engagement sur Instagram

KPIs :
* +20% de reach organique
* +10k abonnés en 1 mois
"""

OUTPUT_DIR = "tests/samples"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "brief_sample.pdf")

class SimplePDF(FPDF):
    def header(self):
        self.set_font("Arial", size=12)
        self.cell(0, 10, "Brief auto-généré", ln=True, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", size=8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def save_pdf_from_md(md_text: str, output_path: str):
    pdf = SimplePDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=11)

    for line in md_text.strip().splitlines():
        pdf.multi_cell(0, 10, line)
    pdf.output(output_path)
    print(f"[OK] PDF écrit à : {output_path}")

if __name__ == "__main__":
    save_pdf_from_md(BRIEF_MD, OUTPUT_PATH)
