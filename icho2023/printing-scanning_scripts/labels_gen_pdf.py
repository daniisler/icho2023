#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   labels_gen_pdf.py
@Time    :   2023/08/02
@Author  :   Daniel Isler
@Contact :   exams@icho2023.ch
@Desc    :   Generates a pdf ready for printing labels on a predefined format (A4, 4x10 labels).
'''

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, mm
import os
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
pdf_tmp_dir = os.path.join(PROJECT_DIR, 'pdf_tmp_dir')
os.makedirs(pdf_tmp_dir, exist_ok=True)

# Open the two csv files containing the data (mg), (g)
df1 = pd.read_csv('/home/daniel/Downloads/labels1.csv', sep=',')
df2 = pd.read_csv('/home/daniel/Downloads/labels2.csv', sep=',')

cm = 10*mm
top_margin = 2.15*cm
left_margin = 0.79*cm
right_margin = 0.79*cm
bottom_margin = 1.45*cm
column_width = 4.85*cm
column_height = 2.54*cm

# How many labels per page
num_horizontal = 4
num_vertical = 10

# Generate a pdf with a grid with margins: top=2.15cm,left=0.79cm,right=0.79cm,bottom=1.45cm and column width=4.85cm, column height=2.54cm
def pdf_grid(grid_text, pdf_idx):
    c = canvas.Canvas(os.path.join(pdf_tmp_dir, f'labels_{pdf_idx}.pdf'), pagesize=A4)
    # Set bold font
    c.setFont("Helvetica-Bold", 18)
    # Calculate the y-coordinate from the top of the page
    page_height = A4[1]
    #print(page_height/column_height)
    y_top = page_height - top_margin - column_height
    for row_idx in range(num_vertical):
        for column_idx in range(num_horizontal):
            if row_idx*4 + column_idx >= len(grid_text):
                break
            # c.rect(left_margin+column_idx*(column_width)+0.5,  y_top - row_idx*(column_height), 4.85*cm, 2.54*cm)
            # Add text inside the rectangle
            text_margin = -0.4
            for text in grid_text[row_idx*4 + column_idx]:
                # Set the text in the middle of the rectangle
                text_x = left_margin+column_idx*(column_width)+0.5 + column_width/2
                text_y = y_top - row_idx*(column_height)  + text_margin*cm + column_height/2
                # Check if text is string
                if isinstance(text, str):
                    c.drawCentredString(text_x, text_y, text)
                    text_margin += 0.8
    c.save()


# Separate the data from the csv files into lists of size 44
data1 = []
data2 = []
pdf_idx = 0
for index, row in df1.iterrows():
    data1.append((f"{row['CaCl2·2H2O - Standard']} mg", row['Chemical']))
    if index%(num_horizontal*num_vertical) == 0 and index != 0:
        pdf_grid(data1, pdf_idx)
        pdf_idx +=1
        data1 = []
pdf_grid(data1, pdf_idx)
pdf_idx +=1

for index, row in df2.iterrows():
    data2.append((f"{round(row['label_weight'], 1)} mg", row['Country code']))
    if index%(num_horizontal*num_vertical) == 0 and index != 0:
        pdf_grid(data2, pdf_idx)
        pdf_idx +=1
        data2 = []
pdf_grid(data2, pdf_idx)
pdf_idx +=1

def merge_pdfs(pdf_paths):
    writer = PdfWriter()
    for pdf in pdf_paths:
        reader = PdfReader(pdf)
        writer.add_page(reader.pages[0])
    writer.write('/home/daniel/Downloads/labels_comb.pdf')

pdf_paths = []
for i in range(pdf_idx):
    pdf_paths.append(os.path.join(pdf_tmp_dir, f'labels_{i}.pdf'))
merge_pdfs(pdf_paths)