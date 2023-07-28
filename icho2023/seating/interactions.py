#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   interactions.py
@Time    :   2023/07/27 21:12:59
@Author  :   George Trenins
@Contact :   gstrenin@gmail.com
@Desc    :   Defines a penalty function for seating certain students
             next to each other based on nationality, spoken languages and other
             relevant parameters.
'''


from __future__ import print_function, division, absolute_import
from icho2023.seating import countries, constants
import numpy as np


class PES(object):

    def __init__(self,
                 sameLR = 10.0, sameSR = [30.0, 20.0, 15.0, 10.0],
                 neighbourLR = 0.0, neighbourSR = [5.0, 3.0, 1.0],
                 languageLR = 0.0, languageSR = [5.0, 3.0, 1.0],
                 otherLR = 0.0, otherSR = [20.0, 15.0, 10.0, 5.0]):
        
        """Penalty function, grading favourability of a student distribution by four types 
        of interactions: 
            * team interaction (students from same country)
            * neighbourhood (students from neighbouring countries)
            * mutual intelligibility (students from countries with shared spoken languages)
            * all other considerations
            
        Each interaction has a  long-range (LR) component, which assigns a fixed penalty
        to two students satisfying a given condition if they are in the same room, regardless
        of relative separation. The short-range (SR) component is calculated assuming a rectilinear
        seating grid. It is assigned by taking the Euclidean distance between two seats
        (steps along rows and columns are both assigned unit length) and rounding 
        to the nearest integer. A distance of i is given the penalty SR[i-1]. 
        """

        self.sameLR = sameLR
        self.sameSR = sameSR
        self.nnLR = neighbourLR
        self.nnSR = neighbourSR
        self.langLR = languageLR
        self.langSR = languageSR
        self.otherLR = otherLR
        self.otherSR = otherSR
        # Maximal range for short-range interactions
        self.maxrange = np.max(
            [len(lst) for lst in [self.sameSR, self.nnSR, self.langSR, self.otherSR]])

    @staticmethod
    def strip_ccode(label):
        """Get the country ISO3 code from a student alphanumeric code.

        Args:
            label (str): e.g., CHE-1

        Returns:
            ISO3: e.g., CHE
        """
        return label[:3]
    
    @staticmethod
    def sum_contributions(site_coeffs, sep):
        """Return the corresponding penalty if students fall within the range
        of a short-range interaction. Otherwise, return zero.

        Args:
            site_coeffs (list): short-range penalties based on site separation
            sep (int): separation of a pair of students

        Returns:
            energy (float)
        """
        energy = 0.0
        if sep <= len(site_coeffs):
            energy += site_coeffs[sep-1]
        return energy
    
    def get_bounds(self, row, col, nrows, ncols):
        """For a student sat on the grid site (`row`, `column`), 
        only part of the entire grid needs to be considered in
        order to calculate the short-range interaction. This function
        returns the bounds of the array section that needs be considered.

        Args:
            row, col (ints): array indices of current seat
            nrows, ncols (ints): total number of seats along the rows and columns
        """
        return ([max(0, row-self.maxrange), min(nrows, row+self.maxrange+1)],
                [max(0, col-self.maxrange), min(ncols, col+self.maxrange+1)])
    
    def energy(self, rooms):
        """Penalty function for a set of examination halls.

        Args:
            rooms (list of ndarrays) : a set of 2D arrays representing
            examination hall seating plans.

        Returns:
            total (float) : penalty score
        """
        total = 0.0
        for room in rooms:
            nrows, ncols = room.shape
            for irow in range(nrows):
                for icol in range(ncols):
                    # Pairwise interaction, avoid double counting
                    total += self.onesite(irow, icol, room)/2
        return total

    def onesite(self, irow, icol, room):
        """Penalty function for a seat at (irow, icol) in the specified room.

        Args:
            irow, icol (int): seat coordinate
            room (ndarray): room plan

        Returns:
            energy (float)
        """
        energy = 0.0
        nrows, ncols = room.shape
        l0 = self.strip_ccode(room[irow, icol])
        if l0 in {'', constants.empty}:
            # Empty seat, no penalty
            return 0.0
        rrange, crange = self.get_bounds(irow, icol, nrows, ncols)
        for jrow in range(nrows):
            for jcol in range(ncols):
                l1 = self.strip_ccode(room[jrow, jcol])
                if l1 in {'', constants.empty}:
                    # Empty seat, no penalty
                    continue
                if irow == jrow and icol == jcol:
                    # No self-interaction
                    continue
                energy += self.lr_pairwise(l0, l1)
                if rrange[0] <= jrow < rrange[1]:
                    if crange[0] <= jcol < crange[1]:
                        energy += self.sr_pairwise(
                            l0, (irow, icol),
                            l1, (jrow, jcol))
        return energy
    
    def twosite(self, row0, col0, room0, row1, col1, room1):
        """Penalty function for two seats, one at (row0, col0)
        room0, the other at (row1, col1) in room1. This is used
        to more efficiently calculate acceptance probabilities
        of Monte Carlo moves.

        Args:
            row0, col0, row1, col1 (int): seat coordinates
            room0, room1 (ndarrays): seating plans

        Returns:
            energy (float)
        """

        ans = (self.onesite(row0, col0, room0) + 
               self.onesite(row1, col1, room1))
        if room0 is room1:
            # Avoid double-counting
            nrows, ncols = room0.shape
            l0 = self.strip_ccode(room0[row0, col0])
            l1 = self.strip_ccode(room1[row1, col1])
            ans -= self.lr_pairwise(l0, l1)
            rrange, crange = self.get_bounds(row0, col0, nrows, ncols)
            if ((rrange[0] <= row1 < rrange[1]) and
                (crange[0] <= col1 < crange[1])):
                ans -= self.sr_pairwise(
                    l0, (row0, col0),
                    l1, (row1, col1)
                )
        return ans

    def sr_pairwise(self, l0, idx0, l1, idx1):
        """Interaction energy for two students in the same room
        seated at coordinates idx0 and idx1

        Args:
            l0, l1 (str): student three-letter country code
            idx0, idx1 (tuple): length-2 tuples specifying the
                seating location
        """
        
        idx0, idx1 = [np.asarray(i) for i in (idx0, idx1)]
        sep = round(np.linalg.norm(idx0-idx1))
        energy = 0.0
        # Team interaction
        if l0 == l1:
            energy += self.sum_contributions(self.sameSR, sep)
            
        # Neighbourhood
        if l1 in countries.nndict[l0]:
            energy += self.sum_contributions(self.nnSR, sep)

        # Mutual intelligibility
        if np.any([(l0 in lset and l1 in lset) for lset in countries.langdict.values()]):
            energy += self.sum_contributions(self.langSR, sep)

        # Other
        try:
            if l1 in countries.other[l0]:
                energy += self.sum_contributions(self.otherSR, sep)
        except KeyError:
            pass

        return energy
    
    def lr_pairwise(self, l0,  l1):
        """Long-range interaction energy for two students 
        in the same room seated at coordinates idx0 and idx1

        Args:
            l0, l1 (str): student three-letter country code
        """
        
        energy = 0.0
        # Self-interaction
        if l0 == l1:
            energy += self.sameLR
            
        # Neighbourhood
        if l1 in countries.nndict[l0]:
            energy += self.b0

        # Mutual intelligibility
        if np.any([(l0 in lset and l1 in lset) for lset in countries.langdict.values()]):
            energy += self.langLR

        # Other
        try:
            if l1 in countries.other[l0]:
                energy += self.otherLR
        except KeyError:
            pass

        return energy