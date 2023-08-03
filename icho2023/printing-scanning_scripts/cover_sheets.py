#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   cover_sheets.py
@Time    :   2023/08/02
@Author  :   Daniel Isler
@Contact :   exams@icho2023.ch
@Desc    :   Generates a cover-sheet that can be used to mark newly printed documents with a code shown through the envelope window.
'''

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, mm
import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Temporary directory for the cover sheets
coversheet_tempdir = os.path.join(PROJECT_DIR, 'coversheet_tempdir')
os.makedirs(coversheet_tempdir, exist_ok=True)
# Position for the text on the cover sheet
# (x, y) position of the rectangle's upper-left corner in mm
position_covertext = (15*mm, 40*mm)
# Define rectangle size in points
width = 91*mm
height = 32*mm

# Generate a new PDF with text at the specified position
def cover_sheet_with_text(text):
    c = canvas.Canvas(os.path.join(coversheet_tempdir, f'cover_{text}.pdf'), pagesize=A4)
    c.setFont("Helvetica", 40*6/len(text))
    x, y = position_covertext
    # Calculate the y-coordinate from the top of the page
    page_height = A4[1]
    y_top = page_height - y
    # Draw the rectangle
    c.rect(x, y_top - height, width, height)
    # Add text inside the rectangle
    text_x = x + 5
    text_y = y_top - height + 5
    c.drawString(text_x, text_y, text)
    c.save()