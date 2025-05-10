#!/usr/bin/env python3
"""
Produit un PDF multi-page avec annexes pour tester robustesse.
"""
import argparse
from pathlib import Path
from scripts.generate_sample_pdf import text_to_pdf, register_font
from reportlab.lib.pagesizes import LETTER

def generate(input_txt: Path, output_pdf: Path, pages: int):
    content = input_txt.read_text(encoding="utf-8")
    content += "\n\n" + "\n\n".join(f"Annexe page {i}" for i in range(1, pages+1))
    tmp = input_txt.parent/"_tmp.txt"
    tmp.write_text(content, encoding="utf-8")
    font = register_font(Path("/Library/Fonts/Arial.ttf"))
    text_to_pdf(tmp, output_pdf, font, LETTER, 72, 14, 85)
    tmp.unlink()
    print(f"[OK] Multi-page PDF généré : {output_pdf}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-i","--input",type=Path,required=True)
    p.add_argument("-o","--output",type=Path,required=True)
    p.add_argument("-p","--pages",type=int,default=5)
    args = p.parse_args()
    generate(args.input,args.output,args.pages)

if __name__=="__main__":
    main()
