#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   make_tables.py
@Time    :   2023/07/23 14:18:04
@Author  :   George Trenins
@Contact :   gstrenin@gmail.com
@Desc    :   None
'''

from __future__ import print_function, division, absolute_import
import pandas as pd
import numpy as np
import argparse
import re
import subprocess
import os
import glob

parser = argparse.ArgumentParser(description="Generate signing sheets by delegation and by student participant.")
parser.add_argument('input', help='Single-column CSV file listing all the student delegates by code.')
args = parser.parse_args()

codes = pd.read_csv(args.input, index_col=None, header=None).to_numpy().ravel()
empty_codes = np.empty_like(codes, dtype=str)
iso3 = np.unique([c[:3] for c in codes])
empty_iso3 = np.empty_like(iso3, dtype=str)

for index, empty, labels, name in zip(
    [codes, iso3],
    [empty_codes,empty_iso3],
    [['Comment'], ['Name', 'Signature']],
    ['code_table.tex', 'delegation_table.tex']
):
    df = pd.DataFrame({r'\multicolumn{1}{|c|}{\textbf{'+key+r'}}':empty for key in labels}, index=index)
    df.index.name = r'\multicolumn{1}{|c|}{\textbf{Code}}'
    df.sort_index(inplace=True)
    df.reset_index(inplace=True)
    n = len(labels)
    res = df.style.hide(axis="index").to_latex(
         column_format='|'.join(['|p{0.75in}']+n*[r'p{{{:.4f}in}}'.format(5.5/n)])+'|', hrules=True)
    res = res.replace(r'\\', r'\\\hline')
    res = res.replace('tabular', 'longtable')
    res = res.replace(r'{:s} \\\hline'.format(df.columns[-1]), 
                      r'{:s} \endhead'.format(df.columns[-1]))
    res = res.replace(r'''\hline
\bottomrule''', r'\bottomrule')
    with open(name, 'w') as f:
        f.write(res)
    with open("sheet_template.tex", "r") as sources:
        lines = sources.readlines()
    texsrc = name.replace('table', 'sheet')
    with open(texsrc, "w") as sources:
        for line in lines:
            sources.write(re.sub(r'@DUMMY@', name, line))
    for i in range(2): subprocess.run(['xelatex', texsrc])
    nameroot = os.path.splitext(texsrc)[0]
    for ext in ['.pdf', '.tex']:
        os.rename(nameroot+ext, '_'+nameroot+ext)
    to_remove = glob.glob(nameroot+'.*')
    for f in to_remove:
        os.remove(f)
    for ext in ['.pdf', '.tex']:
        os.rename('_'+nameroot+ext, nameroot+ext)
