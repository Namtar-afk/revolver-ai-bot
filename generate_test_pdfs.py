#!/usr/bin/env python3
from fpdf import FPDF


def generate_pdf(output_path: str) -> None:
    """
    Génère un PDF de test minimal et l'enregistre sous output_path.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Brief de test", ln=1, align="L")
    pdf.output(output_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Génère un PDF de test")
    parser.add_argument("output", help="Chemin de sortie du PDF")
    args = parser.parse_args()
    generate_pdf(args.output)
