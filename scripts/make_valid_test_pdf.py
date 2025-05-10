#!/usr/bin/env python3
"""
Génère un PDF multi‑page de test à partir d'un .txt, avec X paragraphes par page (alias --pages pour les tests).

Usage:
  python scripts/make_valid_test_pdf.py \
    -i input.txt -o output.pdf [-p PARAS] [--pages PARAS]
"""
import argparse
import textwrap
from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

def txt_to_multipage_pdf(input_path: Path, output_path: Path, paras_per_page: int):
    text = input_path.read_text(encoding="utf-8")
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    c = canvas.Canvas(str(output_path), pagesize=LETTER)
    width, height = LETTER
    margin = 72
    line_h = 14
    font = "Helvetica"
    x = margin
    y = height - margin

    def new_page():
        c.showPage()
        c.setFont(font, 12)

    c.setFont(font, 12)
    for idx, para in enumerate(paragraphs):
        if idx > 0 and idx % paras_per_page == 0:
            new_page()
            y = height - margin
        for line in textwrap.wrap(para, width=80):
            if y < margin:
                new_page()
                y = height - margin
            c.drawString(x, y, line)
            y -= line_h
        y -= line_h

    c.save()
    print(f"[OK] multi‑page PDF généré : {output_path}")

def main():
    p = argparse.ArgumentParser(
        description="Génère un PDF multi‑page de test depuis un .txt"
    )
    p.add_argument(
        "-i", "--input", required=True, type=Path, help="Fichier texte source"
    )
    p.add_argument(
        "-o", "--output", required=True, type=Path, help="PDF de sortie"
    )
    p.add_argument(
        "-p", "--paras", type=int, dest="paras",
        help="Nbr de paragraphes par page",
        default=1
    )
    p.add_argument(
        "--pages", type=int, dest="paras",
        help="Alias --pages pour tests", default=None
    )
    args = p.parse_args()

    # paras déjà fixé par dest alias
    paras = args.paras if args.paras is not None else 1
    txt_to_multipage_pdf(args.input, args.output, paras)

if __name__ == "__main__":
    main()