#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   lab_covers.py
@Time    :   2023/08/05 17:46:42
@Author  :   George Trenins
@Contact :   gstrenin@gmail.com
'''


from __future__ import print_function, division, absolute_import
import pandas as pd
import numpy as np
import os
import glob
import argparse
import subprocess

parser = argparse.ArgumentParser(description="Generate lab inspection cover sheets with delegation-specific lists of assigned lab spaces.")

parser.add_argument('template', help="Path to a TeX template with generic instructions and the markers '@CODE@' and '@TABLE@' which will be replaced with the three-letter delegation code and the corresponding list of labs.")
parser.add_argument('database', help="Path to pandas dataframe in pkl format, containing the entries 'Code' and 'Exam1', listing the three-letter (XXX-0) student codes and corresponding practical exam venues.")
parser.add_argument('-o', '--output', default="lab_covers.pdf", help="Name of output PDF.")

args = parser.parse_args()
df = pd.read_pickle(args.database)
with open(args.template, 'r') as f:
    tex = f.readlines()
tex = "".join(tex)

header, rest = tex.split(r"\begin{document}",1)
header += r"\begin{document}"+'\n'
body, footer = rest.split(r"\end{document}")
footer = r"\end{document}"+'\n'+footer

df.reset_index(inplace=True)

codes = df["Code"]
countries = np.sort(np.unique([code[:3] for code in codes]))
target = "_"+os.path.splitext(args.output)[0]
with open(target+".tex", "w") as f:
    f.write(header)
    for code in countries:
        # Fetch correct delegation
        labs = df[df['Code'].str.match(code)][["Code", "Exam1"]]
        # Set up correct column titles and formatting
        labs.sort_values(by=["Code"], inplace=True)
        labs.rename(columns={'Exam1' : 'Lab'}, inplace=True)
        labs["Notes"] = np.empty_like(labs["Code"].to_numpy(), dtype=str)
        old_labels = ['Code', 'Lab', 'Notes']
        new_labels = [r'\multicolumn{1}{|c|}{\textbf{'+key+r'}}' for key in old_labels]
        labs.rename(columns={key : val for key,val in zip(old_labels, new_labels)}, inplace=True)
        # Replace underscore with hyphen - looks nicer in print
        labs.replace(to_replace = r'_', value = r'-', regex=True, inplace=True)
        # Fine tune table appearance
        res = labs[new_labels].style.hide(axis="index").to_latex(
            column_format='|p{0.75in}|p{1.25in}|X|', hrules=True)
        res = res.replace(r'\\', r'\\\hline')
        res = res.replace(r'\begin{tabular}', r'\begin{tabularx}{\textwidth}')
        res = res.replace(r'\end{tabular}', r'\end{tabularx}')
        res = res.replace(r'{:s} \\\hline'.format(labs.columns[-1]), 
                        r'{:s} \\'.format(labs.columns[-1]))
        res = res.replace(r'''\hline
\bottomrule''', r'\bottomrule')
        # Replace dummy strings with delegation-specific content
        f.write(body.replace('@CODE@', code).replace('@TABLE@',res))
        f.write("\clearpage\n")
    f.write(footer)

subprocess.call(['xelatex', target+'.tex'])
subprocess.call(['xelatex', target+'.tex'])

os.rename(target+'.pdf', args.output)
to_remove = glob.glob(target+'*')
for f in to_remove:
    os.remove(f)