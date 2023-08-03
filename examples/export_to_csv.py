#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   make_database.py
@Time    :   2023/06/24 12:37:15
@Author  :   George Trenins
@Contact :   gstrenin@gmail.com
@Desc    :   Convert pkl database back to csv
'''

from __future__ import print_function, division, absolute_import
import pandas as pd
import argparse
from icho2023.seating import countries

parser = argparse.ArgumentParser()
parser.add_argument("pkl", help="Name of pickle file storing the dataframe")
parser.add_argument("out", help="Path to output CSV file to store information on students. The first columns should be the Country and the ISO3 code. Then follow four groups of 'Code', 'Exam1', 'Exam2', one per student (may be empty)")
args = parser.parse_args()

df = pd.read_pickle(args.pkl)
# Make the index (code) into a column
df.reset_index(inplace=True)
iso3 = [df.loc[i,"Code"][:3] for i in range(len(df))]
df['ISO3'] = iso3
country_names = [countries.code2name(c) for c in iso3]
df['Country'] = country_names
# Split into dataframe by student number
splitdf = []
names = []
cols = ['Code', 'Exam1', 'Exam2' ]
for i in range(1,5):
    names.append(f'Student-{i}')
    idf = df.loc[df.Code.str.contains(f'-{i}')].set_index('Country')
    if i == 1:
        iso3 = idf.pop('ISO3')
    else:
        idf.drop(columns='ISO3')
    splitdf.append(idf[cols])



stitchdf = pd.concat([iso3,]+splitdf, keys=["",]+names, axis=1)
stitchdf.sort_index(inplace=True)
stitchdf.reset_index(inplace=True)
stitchdf.to_csv(args.out, index=False)
