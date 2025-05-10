from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

content = '''
BRIEF CLIENT

Problème
La marque souffre d’un manque de notoriété chez les 18–25 ans, malgré une présence sur les réseaux sociaux.

Objectifs
1. Générer de la visibilité sur TikTok.
2. Augmenter l’engagement sur Instagram.
3. Renforcer l’image de marque autour des valeurs éthiques.

KPIs
- +20% de reach sur TikTok.
- 10 000 interactions sur Instagram.
- Notoriété top of mind mesurée via étude YouGov.
'''.strip()

c = canvas.Canvas("tests/samples/brief_sample.pdf", pagesize=LETTER)
for i, line in enumerate(content.split("\n")):
    c.drawString(72, 750 - 15 * i, line)
c.save()
