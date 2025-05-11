#!/usr/bin/env python3
"""
Génère un PDF multi-pages pour tester le parsing.
Usage :
  python scripts/make_valid_test_pdf.py -i input.txt -o output.pdf [-p N]
"""
import argparse, textwrap
from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

def txt_to_multipage_pdf(txt: Path, pdf: Path, pages: int, margin=72, linewidth=85):
    lines = txt.read_text(encoding="utf-8").splitlines()
    all_lines = lines * pages  # duplique le contenu

    c = canvas.Canvas(str(pdf), pagesize=LETTER)
    width, height = LETTER
    font_size, leading = 12, 14
    x, y = margin, height - margin
    c.setFont("Helvetica", font_size)

    for line in all_lines:
        for frag in textwrap.wrap(line, width=linewidth):
            if y < margin + leading:
                c.showPage()
                c.setFont("Helvetica", font_size)
                y = height - margin
            c.drawString(x, y, frag)
            y -= leading
    c.save()
    print(f"[OK] multi-page PDF généré : {pdf}")

def main():
    p = argparse.ArgumentParser(description="Génère un PDF multi-pages pour tests.")
    p.add_argument("-i","--input", required=True, type=Path, help="Fichier .txt source")
    p.add_argument("-o","--output", required=True, type=Path, help="Fichier .pdf de sortie")
    p.add_argument("-p","--pages", type=int, default=1, help="Nombre de pages")
    args = p.parse_args()
    txt_to_multipage_pdf(args.input, args.output, args.pages)

if __name__=="__main__":
    main()
