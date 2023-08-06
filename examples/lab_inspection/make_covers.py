#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   make_covers.py
@Time    :   2023/07/08 18:52:08
@Author  :   George Trenins
@Contact :   gstrenin@gmail.com
@Desc    :   None
'''


from __future__ import print_function, division, absolute_import
import pandas as pd
import os
import numpy as np
rootdir = os.path.abspath(__file__)
for i in range(3):
    rootdir = os.path.dirname(rootdir)
datafile = os.path.join(rootdir,"Seating","finals","SeatedStudents2.pkl")
print(datafile)
df = pd.read_pickle(datafile)

texfile = open('covers.tex', 'w')

header = r"""\documentclass[12pt,a4paper]{article}
\usepackage[document]{ragged2e}
\usepackage{fontspec}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{lastpage}
\usepackage{ulem}
\usepackage{tabularx}
\usepackage{graphicx}
\usepackage{wrapfig}
\usepackage[absolute, overlay]{textpos}
\usepackage[includehead,
nomarginpar,% We don't want any margin paragraphs
headheight=22mm,% 
margin=2cm,
top=1cm
]{geometry}
\usepackage{fancyhdr}
\setmainfont{AvenirNextLTPro-Cn.ttf}[
BoldFont = AvenirNextLTPro-BoldCn.ttf ,
Path = /home/george/Documents/Olympiad_Working_Group/2023/CH_committee/Print_and_Publish/IChO2023_CorporateDesign/03_IChO2023_Visitenkarte/fonts/]
\newlength{\mylength}

\begin{document}
	\pagestyle{fancy}
	\fancyhf{} % clear existing header/footer entries
	% We don't need to specify the O coordinate
	\fancyhead[L]{\includegraphics[height=20mm]{IChO2023_Logo_Title_L_CMYK.eps}}
\setlength{\parindent}{0pt}
\setlength\intextsep{0pt}
\setlength{\mylength}{-2em}




"""

texfile.write(header)

body_code = r"""
	\begin{{textblock*}}{{8cm}}(20mm,47mm) 
		\centering \bfseries \rule[-6.5mm]{{0pt}}{{30mm}}
		{{\fontsize{{70}}{{85}}\selectfont {code}}}
	\end{{textblock*}}

	\begin{{textblock*}}{{7cm}}(117mm,53mm)
		Welcome to the 55\textsuperscript{{th}} IChO,\\[1.5ex]
		
    """

body_labs = [
	r"""Your student has been allocated to the following
    laboratory in the HCI building:
 	\end{{textblock*}}

\vspace*{{44mm}}

\renewcommand{{\arraystretch}}{{1.5}}
\begin{{tabularx}}{{\textwidth}}{{p{{2cm}}p{{2cm}}X}}
	\toprule
	\textbf{{Code}} & \textbf{{Lab}} & \textbf{{Notes}} \\
	\midrule
	\rule[\mylength]{{0pt}}{{0pt}}%
	{:s}         & {:s}       &        \\
	\bottomrule
\end{{tabularx}}""",
	r"""Your students have been allocated to the following
    laboratories in the HCI building:
 	\end{{textblock*}}

\vspace*{{44mm}}

\renewcommand{{\arraystretch}}{{1.5}}
\begin{{tabularx}}{{\textwidth}}{{p{{2cm}}p{{2cm}}X}}
	\toprule
	\textbf{{Code}} & \textbf{{Lab}} & \textbf{{Notes}} \\
	\midrule
	\rule[\mylength]{{0pt}}{{0pt}}%
	{:s}         & {:s}       &        \\\hline
	\rule[\mylength]{{0pt}}{{0pt}}%
	{:s}         & {:s}       &        \\
	\bottomrule
\end{{tabularx}}""",
	r"""Your students have been allocated to the following
    laboratories in the HCI building:
 	\end{{textblock*}}

\vspace*{{44mm}}

\renewcommand{{\arraystretch}}{{1.5}}
\begin{{tabularx}}{{\textwidth}}{{p{{2cm}}p{{2cm}}X}}
	\toprule
	\textbf{{Code}} & \textbf{{Lab}} & \textbf{{Notes}} \\
	\midrule
	\rule[\mylength]{{0pt}}{{0pt}}%
	{:s}         & {:s}       &        \\\hline
	\rule[\mylength]{{0pt}}{{0pt}}%
	{:s}         & {:s}       &        \\\hline
	\rule[\mylength]{{0pt}}{{0pt}}%
	{:s}         & {:s}       &        \\
	\bottomrule
\end{{tabularx}}""",
	r"""Your students have been allocated to the following
    laboratories in the HCI building:
 	\end{{textblock*}}

\vspace*{{44mm}}

\renewcommand{{\arraystretch}}{{1.5}}
\begin{{tabularx}}{{\textwidth}}{{p{{2cm}}p{{2cm}}X}}
	\toprule
	\textbf{{Code}} & \textbf{{Lab}} & \textbf{{Notes}} \\
	\midrule
	\rule[\mylength]{{0pt}}{{0pt}}%
	{:s}         & {:s}       &        \\\hline
	\rule[\mylength]{{0pt}}{{0pt}}%
	{:s}         & {:s}       &        \\\hline
	\rule[\mylength]{{0pt}}{{0pt}}%
	{:s}         & {:s}       &        \\\hline
	\rule[\mylength]{{0pt}}{{0pt}}%
	{:s}         & {:s}       &        \\
	\bottomrule
\end{{tabularx}}""",
]
		
body_rest = r"""
\vspace*{{2em}}

\begin{{wrapfigure}}{{R}}{{0.5\textwidth}}
	\centering
	\includegraphics[width=0.95\linewidth]{{plan.pdf}}
\end{{wrapfigure}}
To proceed with the laboratory inspection, please take the stairs
down from the HPH building where you have received these instructions and turn left as indicated on the plan. Having reached the meeting
point marked with a blue diamond, follow the signposts directing you
to your designated laborator{:s}. A volunteer will be on hand at the 
meeting point should you have any questions or if you need help with
directions. Once the inspection is complete, \uline{{return to the HPH building
and sign a sheet}} confirming the proper setup of student workbenches.
You will then receive a pre-print of the practical examination and
OlyExams login credentials.

\vspace*{{1em}}

At HPH, you will also have the opportunity to request a printout of
your students' worksheets, available for collection from the
Crowne Plaza Hotel on the morning of 22 July, the day before arbitration. However, we would appreciate it if you helped
us minimize our paper usage by utilizing the electronic versions that will become available through OlyExams. Let's work together to reduce our ecological footprint and make the International Chemistry Olympiad more sustainable.

\vspace*{{1em}}

When you are ready to go back to the hotel, please proceed to the 
bus stop indicated on the plan and take bus number 80 in the direction
of Triemlispital. At Lindenplatz, change to tram number 2 going to
Bahnhof Tiefenbrunnen and ride four stops, getting off at Letzigrund, 
which is within a three-minute walk from your final destination.

               

"""

footer = r"""

\end{document}
"""

# Apply aliases
df.replace(to_replace={'BLR':'QMC', 'RUS':'QMP'}, inplace=True)
countries = np.unique(df.ISO3)

for code in countries:
	labs = df[df['ISO3'].str.match(code)].Exam1.to_list()
	labs = [l[4:] for l in labs]
	isos = df[df['ISO3'].str.match(code)].index.to_list()
	texfile.write(body_code.format(code=code))
	n = len(labs) - 1
	texfile.write(body_labs[n].format(*(val for pair in zip(isos, labs) for val in pair)))
	texfile.write(body_rest.format("y" if n == 0 else "ies"))
	texfile.write(r"""
               
\clearpage
               
               """)
        
texfile.write(footer)
texfile.close()
    
