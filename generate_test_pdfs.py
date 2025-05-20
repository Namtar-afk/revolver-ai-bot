from fpdf import FPDF
import os

os.makedirs("tests/samples", exist_ok=True)

def create_pdf(filename, text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output(filename)

create_pdf("tests/samples/brief_simple.pdf", "Titre: Brief Simple\nObjectifs:\n- Objectif 1\n- Objectif 2\nRésumé: Ceci est un brief simple de test.")
create_pdf("tests/samples/brief_multi.pdf", "Titre: Brief Multi\nObjectifs:\n- Objectif A\n- Objectif B\nRésumé: Ceci est un brief multi-page de test.")
