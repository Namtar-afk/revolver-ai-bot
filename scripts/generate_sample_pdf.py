#!/usr/bin/env python3
"""
Génère un PDF paginé depuis un .txt (UTF-8).

Usage:
  scripts/generate_sample_pdf.py \
    -i path/to/input.txt \
    -o path/to/output.pdf \
    [--font path/to/font.ttf] \
    [--pagesize LETTER|A4] \
    [--margin 72] \
    [--linewidth 85]
"""
import argparse
import textwrap
from pathlib import Path

from reportlab.lib.pagesizes import A4, LETTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def register_font(font_path: Path | None, name: str = "CustomFont") -> str:
    """
    Si --font pointe vers un .ttf valide, l'enregistre sous `name`.
    Sinon, on utilise "Helvetica" (native, pas besoin de l'enregistrer).
    """
    if font_path:
        font_path = Path(font_path)
        if font_path.is_file():
            try:
                pdfmetrics.registerFont(TTFont(name, str(font_path)))
                return name
            except Exception:
                pass
    # Helvetica, Times-Roman, Courier sont disponibles par défaut
    return "Helvetica"


def txt_to_pdf(
    input_path: Path,
    output_path: Path,
    pagesize,
    margin: int,
    linewidth: int,
    font_name: str,
):
    text = input_path.read_text(encoding="utf-8")
    c = canvas.Canvas(str(output_path), pagesize=pagesize)
    c.setFont(font_name, 12)
    _, height = pagesize
    x, y = margin, height - margin

    for paragraph in text.split("\n\n"):
        for raw_line in paragraph.split("\n"):
            for line in textwrap.wrap(raw_line, width=linewidth) or [""]:
                if y < margin + 14:
                    c.showPage()
                    c.setFont(font_name, 12)
                    y = height - margin
                c.drawString(x, y, line)
                y -= 14
        # saut de paragraphe
        y -= 14
        if y < margin + 14:
            c.showPage()
            c.setFont(font_name, 12)
            y = height - margin

    c.save()


def main():
    p = argparse.ArgumentParser(
        description="Génère un PDF paginé à partir d'un .txt (UTF-8)."
    )
    p.add_argument(
        "-i", "--input", type=Path, required=True, help="Fichier .txt source (UTF‑8)"
    )
    p.add_argument("-o", "--output", type=Path, required=True, help="PDF de sortie")
    p.add_argument(
        "--font", type=Path, help="(Optionnel) Chemin vers une police .ttf Unicode"
    )
    p.add_argument(
        "--pagesize",
        choices=["LETTER", "A4"],
        default="LETTER",
        help="Format de page (LETTER ou A4)",
    )
    p.add_argument(
        "--margin", type=int, default=72, help="Marge en points (72 = 1 pouce)"
    )
    p.add_argument("--linewidth", type=int, default=85, help="Max caractères par ligne")
    args = p.parse_args()

    font_name = register_font(args.font, "CustomFont")
    pagesize = LETTER if args.pagesize == "LETTER" else A4

    txt_to_pdf(
        input_path=args.input,
        output_path=args.output,
        pagesize=pagesize,
        margin=args.margin,
        linewidth=args.linewidth,
        font_name=font_name,
    )
    print(f"[OK] PDF généré : {args.output}")


if __name__ == "__main__":
    main()
