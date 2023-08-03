#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   countries.py
@Time    :   2023/03/16 21:46:50
@Author  :   George Trenins
@Contact :   gstrenin@gmail.com
@Desc    :   Data on country naming, neighbourhood and compatibility
'''


from __future__ import print_function, division, absolute_import
from os import path
from icho2023.seating.constants import datadir, aliases, empty
import pandas as pd
import numpy as np
import json

_nanvals = ['', 'NULL', 'NaN']
# Dataset of invitees + languages
invitedf = pd.read_csv(path.join(datadir, 'invitees.csv'), index_col=0, keep_default_na=False, na_values=_nanvals)
invitedf.index = invitedf.index.str.lower()
# Dataset relating country name to two- and three-letter codes
iso3df = pd.read_csv(path.join(datadir, 'iso3166.csv'), index_col=0, keep_default_na=False, na_values=_nanvals)
iso3df.index = iso3df.index.str.lower()
iso3df["Code"] = iso3df["Alpha-3"]
# Dataset of land borders (listed pairwise)
neighbours = pd.read_csv(path.join(datadir, 'borders.csv'), index_col=None, usecols=[0,2], keep_default_na=False, na_values=_nanvals)

# Replace ISO3 codes with aliases whenever appropriate
col = "Code"
for key in aliases:
    iso3df.loc[ iso3df[col] == key, col] = aliases[key]

def two2code(iso):
    """Convert two-letter iso3166-1 designation to IChO 3-letter code 
    """
    return iso3df.loc[iso3df["Alpha-2"] == iso,"Code"].iloc[0]

def code2two(code):
    """Convert IChO 3-letter code to two-letter iso3166-1 designation
    """
    return iso3df.loc[iso3df["Code"] == code,"Alpha-2"].iloc[0]

def name2code(country):
    """Return the three-letter code for the requested country."""
    return iso3df.loc[country.lower().strip(), "Code"]
    
def add_relation(d, country, *args, coded=False):
    """The input dictionary `d` contains country codes as keys, e.g. 'CHE'.
    The corresponding values are sets of country codes with which the key
    is in a certain relationship. For example, if the relationship is
    language, then the value for 'CHE' might be {'DEU', 'AUT', 'ITA'}.
    We might want to add France (FRA) and Luxembourg (LUX). This function
    ensures that when this is done, the reciprocal relation is also
    recorded ('CHE' is added to the sets associated with 'FRA' and 'LUX')
    
    Args:
        d (dict) : dictionary recording an inter-country relationship
        country (str) : three-letter country code or name of country, for
            which the relationship is augmented
        args : three-letter country codes or names to be added to the
            relationship
        coded (bool, optional) : whether `country` and `args` are given
            as codes. The default is False, in which case it is assumed
            the input is country names, which needs to be translated.
    """
    country_code = country if coded else name2code(country)
    for c in args:
        # Iterate over countries to be included in the relationship
        arg_code = c if coded else name2code(c)
        try:
            # Is the relationship already documented?
            listed = arg_code in d[country_code]
        except KeyError:
            # Root country not present in dictionary - add it
            d[country_code] = set()
            listed = False
        if not listed:
            d[country_code] = d[country_code].union(set([arg_code]))
            add_relation(d, arg_code, country_code, coded=True)

# Nearest-neighbour lists (land-only)
nndict = dict()
for land in invitedf.index:
    code = name2code(land)
    two = code2two(code)
    nndf = neighbours.query(f"country_code == '{two}'")['country_border_code']
    notempty = np.all(nndf.notna())
    if notempty:
        nnlist = nndf.to_list()
        add_relation(nndict, code, *( two2code(t) for t in nnlist ), coded=True)
    else:
        nndict[code] = set()
# Add non-interacting empty item
nndict[empty] = set()
# Add important sea borders
with open(path.join(datadir,'extra_borders.json'), 'r') as f:
    od = json.load(f)
for key in od:
    add_relation(nndict, key, *od[key])

# Common language lists - make a dictionary of langauges,
# and countries where they are commonly spoken. This 
# list is incomplete, as it only takes account of the
# official language(s) - better results may be achieved by
# using information on spoken languages collected on 
# registration
langdict = dict()
for key in invitedf.index:
    code = name2code(key)
    langs = invitedf.loc[key, ["Language 1", "Language 2", "Language 3"]]
    langs = langs.to_numpy()[langs.notna()]
    for lang in langs:
        if lang in langdict:
            langdict[lang] = langdict[lang].union({code})
        else:
            langdict[lang] = {code}

# Can ignore sets of one:
keys = list(langdict)
for key in keys:
    if len(langdict[key]) == 1:
        langdict.pop(key)

# Other interactions, based on https://www.cfr.org/global-conflict-tracker/
# as of May 2023. This is not an expression of a political opinion and must
# not be treated as such. The relations documented here are most prone
# to change and can be modified however the organisers see fit.

other = dict()
with open(path.join(datadir,'other.json'), 'r') as f:
    od = json.load(f)
for key in od:
    add_relation(other, key, *od[key])

if __name__ == "__main__":

    # Run some quick tests
    print("Country codes:")
    print("Switzerland: ", name2code('Switzerland'))
    print()
    print("Nearest neighbours:")
    print("Denmark: ", nndict[name2code('Denmark')])
    print("Kuwait: ", nndict[name2code('Kuwait')])
    print("Nepal: ", nndict[name2code('Nepal')])
    print()
    print("Intelligibility sets:")
    for key in langdict:
        print(f'{key}: {langdict[key]}')
    print()
    print("Other sets:")
    for key in other:
        print(f'{key}: {other[key]}')