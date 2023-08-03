#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   assign_codes.py
@Time    :   2023/08/03 11:45:29
@Author  :   George Trenins
@Contact :   gstrenin@gmail.com
'''


from __future__ import print_function, division, absolute_import
import pandas as pd
import argparse
import numpy as np
from os import path
from icho2023.seating.constants import datadir
from icho2023.seating.countries import name2code, _nanvals


parser = argparse.ArgumentParser(description="Generate a single-column text file listing all the student participant codes")
parser.add_argument('-i', '--input', default=None, help='Path to a CSV file listing the country of the attending delegations in the first column and the number of students in the second column. If not specified, will read "invitees.csv" from the `data` directory.')
parser.add_argument('-o', '--output', default='codes.csv', help='Name of the output file.')

args = parser.parse_args()

invitees = path.join(datadir, 'invitees.csv') if args.input is None else args.input
invitedf = pd.read_csv(invitees, index_col=0, keep_default_na=False, na_values=_nanvals)
codes = []
for index, row in invitedf.iterrows():
    codes.append([f'{name2code(index)}-{i+1}' for i in range(row.Students)])
df = pd.DataFrame(np.concatenate(codes))
df.to_csv(args.output, header=False, index=False)

