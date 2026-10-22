#!/usr/bin/env python3
"""One-page PDF freebie for a reel keyword.

Usage: python3 freebie.py <reel-folder>/freebie.json <out.pdf>

freebie.json: {"title": "...", "subtitle": "...", "sections": [{"heading": "...", "items": ["...", ...],
               "numbered": true}], "footer": "..."}
Every line must come from the script or the messaging bank (USE/SOURCED only). No new claims.
"""
import json
import sys

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

pdfmetrics.registerFont(TTFont('Sans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('Sans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFontFamily('Sans', normal='Sans', bold='Sans-Bold', italic='Sans', boldItalic='Sans-Bold')

INK, MUTED, ACCENT = HexColor('#111111'), HexColor('#555555'), HexColor('#FECB00')
spec = json.load(open(sys.argv[1]))
title = ParagraphStyle('t', fontName='Sans-Bold', fontSize=24, leading=29, textColor=INK, spaceAfter=6)
sub = ParagraphStyle('s', fontName='Sans', fontSize=12, leading=16, textColor=MUTED, spaceAfter=18)
head = ParagraphStyle('h', fontName='Sans-Bold', fontSize=14, leading=18, textColor=INK, spaceBefore=10, spaceAfter=8)
body = ParagraphStyle('b', fontName='Sans', fontSize=11, leading=15, textColor=INK)
foot = ParagraphStyle('f', fontName='Sans', fontSize=9, leading=12, textColor=MUTED, spaceBefore=8)

story = [Paragraph(spec['title'], title)]
if spec.get('subtitle'):
    story.append(Paragraph(spec['subtitle'], sub))
for sec in spec['sections']:
    story.append(Paragraph(sec['heading'], head))
    rows = []
    for i, item in enumerate(sec['items'], 1):
        mark = str(i) if sec.get('numbered') else '✓'
        rows.append([Paragraph(f'<b>{mark}</b>', ParagraphStyle('m', parent=body, alignment=1)), Paragraph(item, body)])
    t = Table(rows, colWidths=[26, 440])
    t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BACKGROUND', (0, 0), (0, -1), ACCENT),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 7), ('TOPPADDING', (0, 0), (-1, -1), 5),
                           ('LINEBELOW', (1, 0), (1, -2), 0.25, HexColor('#DDDDDD'))]))
    story.append(t)
    story.append(Spacer(1, 6))
story.append(Paragraph(spec.get('footer', 'Andy Pham · BusinessGrowR'), foot))
SimpleDocTemplate(sys.argv[2], pagesize=letter, leftMargin=54, rightMargin=54, topMargin=40, bottomMargin=40,
                  title=spec['title'], author='BusinessGrowR').build(story)
print('wrote', sys.argv[2])
