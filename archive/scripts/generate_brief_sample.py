# scripts/generate_brief_sample.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_sample_pdf(path="tests/samples/brief_sample.pdf"):
    c = canvas.Canvas(path, pagesize=A4)
    text = c.beginText(50, 800)
    text.setFont("Helvetica", 12)
    text_lines = [
        "TITRE STATIC", "",
        "Problème",
        "Brief statique pour les tests d’intégration.", "",
        "Objectifs",
        "Test statique.", "",
        "KPIs",
        "- TEST1"
    ]
    for line in text_lines:
        text.textLine(line)
    c.drawText(text)
    c.showPage()
    c.save()

if __name__ == "__main__":
    generate_sample_pdf()

