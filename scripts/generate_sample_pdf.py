#!/usr/bin/env python3
"""
Génère un PDF “brief” paginé Unicode à partir d’un .txt / .md
Usage :
  python scripts/generate_sample_pdf.py -i input.txt -o output.pdf
"""
import argparse, textwrap
from pathlib import Path
from reportlab.lib.pagesizes import LETTER, A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def register_font(ttf_path: Path, name: str="CustomFont") -> str:
    pdfmetrics.registerFont(TTFont(name, str(ttf_path)))
    return name

def text_to_pdf(input_path: Path, output_path: Path,
                font_name: str, pagesize, margin: int,
                line_height: int, max_chars: int):
    text = input_path.read_text(encoding="utf-8")
    c = canvas.Canvas(str(output_path), pagesize=pagesize)
    c.setFont(font_name, 12)
    w, h = pagesize
    x, y = margin, h - margin
    for paragraph in text.split("\n\n"):
        for line in paragraph.split("\n"):
            for wrapped in textwrap.wrap(line, max_chars) or [""]:
                if y < margin + line_height:
                    c.showPage()
                    c.setFont(font_name, 12)
                    y = h - margin
                c.drawString(x, y, wrapped)
                y -= line_height
        y -= line_height
        if y < margin + line_height:
            c.showPage()
            c.setFont(font_name, 12)
            y = h - margin
    c.save()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-i","--input", type=Path, required=True)
    p.add_argument("-o","--output",type=Path,default=Path("brief.pdf"))
    p.add_argument("-f","--font", type=Path,
                   default=Path("/Library/Fonts/Arial.ttf"))
    p.add_argument("-s","--pagesize",choices=["LETTER","A4"],default="LETTER")
    p.add_argument("-m","--margin",type=int,default=72)
    p.add_argument("-w","--linewidth",type=int,default=85)
    args = p.parse_args()

    pagesize = LETTER if args.pagesize=="LETTER" else A4
    font = register_font(args.font)
    text_to_pdf(args.input,args.output,font,pagesize,
                args.margin,14,args.linewidth)
    print(f"[OK] PDF généré : {args.output}")

if __name__=="__main__":
    main()
