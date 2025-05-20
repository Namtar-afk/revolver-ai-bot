#!/usr/bin/env python3
"""
Convertit un fichier texte en PDF “brief” paginé, avec une police built-in
pour garantir une extraction fiable de texte (pdfminer compatible).

Usage :
  python scripts/generate_brief_pdf.py \
    --input tests/samples/brief_multi.txt \
    --output tests/samples/brief_multi.pdf \
    [--pagesize LETTER|A4] \
    [--margin 72] \
    [--linewidth 85]
"""

import argparse
import textwrap
import sys
from pathlib import Path

from reportlab.lib.pagesizes import LETTER, A4
from reportlab.pdfgen import canvas


def text_to_pdf(
    input_path: Path,
    output_path: Path,
    pagesize,
    margin: int,
    line_height: int,
    max_chars: int,
):
    text = input_path.read_text(encoding="utf-8")
    c = canvas.Canvas(str(output_path), pagesize=pagesize)
    c.setFont("Helvetica", 12)  # Built-in font = extractible

    width, height = pagesize
    x = margin
    y = height - margin

    for paragraph in text.split("\n\n"):
        for raw_line in paragraph.split("\n"):
            wrapped = textwrap.wrap(raw_line, max_chars) or [""]
            for line in wrapped:
                if y < margin + line_height:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y = height - margin
                c.drawString(x, y, line)
                y -= line_height
        y -= line_height
        if y < margin + line_height:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - margin

    c.save()


def main():
    p = argparse.ArgumentParser(
        description="Transforme un brief .txt en PDF paginé (StandardEncoding pour extraction fiable)."
    )
    p.add_argument("-i", "--input", type=Path, required=True,
                   help="Chemin vers le fichier source (.txt, .md…)")
    p.add_argument("-o", "--output", type=Path,
                   default=Path("tests/samples/brief_generated.pdf"),
                   help="Chemin de sortie du PDF")
    p.add_argument("-s", "--pagesize", choices=["LETTER", "A4"],
                   default="LETTER", help="Format de page")
    p.add_argument("-m", "--margin", type=int, default=72,
                   help="Marge en points (72 = 1 pouce)")
    p.add_argument("-w", "--linewidth", type=int, default=85,
                   help="Nombre max de caractères par ligne")
    args = p.parse_args()

    try:
        size = LETTER if args.pagesize == "LETTER" else A4
        text_to_pdf(
            input_path=args.input,
            output_path=args.output,
            pagesize=size,
            margin=args.margin,
            line_height=14,
            max_chars=args.linewidth,
        )
        print(f"[OK] PDF généré (extractible) : {args.output}")
    except Exception as e:
        print(f"[ERREUR] génération échouée : {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
