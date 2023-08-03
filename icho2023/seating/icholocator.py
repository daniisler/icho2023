#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   icholocator.py
@Time    :   2023/07/28 22:53:39
@Author  :   George Trenins
@Contact :   gstrenin@gmail.com
@Desc    :   Seat the students to minimise adverse interaction using a simulated annealing algorithm.
'''


from __future__ import print_function, division, absolute_import
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import logging


class MCSimulation(object):

    def __init__(self, rooms, beta, PES, students=None,
                 idum=1, shuffle=False):
        """Run a Monte Carlo simulation to optimise student distribution by room

        Args:
            rooms (list of Halls): available seating
            beta (float): reciprocal simulation thermal energy
            PES (object): merit function
            students (Students, optional): participants to distribute. 
                If None, read from rooms.
            idum (int, optional): Seed for random number generator.
                Defaults to 1.
            shuffle (bool): set to True if students are to be  
                shuffled before distributing between halls upon
                initialisation.
        """

        self.rooms = rooms
        self.rng = np.random.default_rng(seed=idum)
        self.PES = PES
        self.beta = beta
        if students is None:
            self.read_rooms()
        else:
            self.populate_rooms(students, shuffle=shuffle)

    def read_rooms(self):
        # Dictionary linking student IDs to room and seat
        student_dict = {"id" : [], "room idx" : [], 
                        "row" : [], "col" : []}
        for iroom, r in enumerate(self.rooms):
            for irow, row in enumerate(r.array):
                for icol, code in enumerate(row):
                    if code == '':
                        continue
                    student_dict['id'].append(code)
                    student_dict["room idx"].append(iroom)
                    student_dict["row"].append(irow)
                    student_dict["col"].append(icol)
        self.students = pd.DataFrame(data=student_dict)

    def populate_rooms(self, students, shuffle):
        # List of arrays representing floor plans
        rooms = [np.reshape(room.array.T, -1) for room in self.rooms]
        # Total number of rooms
        nrooms = len(rooms)
        # Mask for allowed seating
        bools = [np.reshape(room.allowed.T, -1) for room in self.rooms]
        # List of flat arrays representing allowed seats for each room
        seats = [np.empty(dtype='<U5', shape=np.count_nonzero(b)) 
                 for b in bools]
        for seat, r in zip(seats, self.rooms):
            seat[:] = r._empty_marker
        maxseats = np.max([s.size for s in seats])
        # shuffle students
        if shuffle:
            students = self.rng.permutation(students)
        # Fill up available seating
        i_student = 0
        i_room = 0
        for i_seat in range(nrooms * maxseats):
            idx = i_seat // nrooms
            try:
                l = students[i_student].id
            except IndexError:
                break
            try:
                seats[i_room%nrooms][idx] = l
            except IndexError:
                i_room += 1
            else:
                i_student += 1
                i_room += 1

        if i_student != len(students):
            raise RuntimeError("Insufficient seating, could only allocate {:d} out of {:d} students".format(i_student, len(students)))
        
        # Fill up original room arrays
        for (r,b,s) in zip(self.rooms, bools, seats):
            tmp = np.empty(dtype='<U5', shape=r.array.size)
            tmp[b] = s
            r.array[:] = np.reshape(tmp, r.array.shape[::-1]).T

        self.read_rooms()

    @property
    def energy(self):
        return self.PES.energy(self.rooms)
    
    def step(self, s=1):
        for i in range(s):
            idx0, idx1 = self.rng.choice(
                len(self.students.index), size=2, replace=False)
            self.attempt(idx0, idx1)
    
    def attempt(self, idx0, idx1):
        row0, col0, _, room0 = self.get_coords(idx0)      
        row1, col1, _, room1 = self.get_coords(idx1)
        oldE = self.PES.twosite(row0, col0, room0, row1, col1, room1)
        # Attempt the swap:
        self.swap(idx0, idx1)
        newE = self.PES.twosite(row0, col0, room0, row1, col1, room1)
        prob = np.exp(-self.beta*(newE - oldE))
        rand = self.rng.uniform()
        if rand > prob:
            # reject
            self.swap(idx0, idx1)

    def get_coords(self, idx):
        i, j, k = self.students.loc[idx, ["row", "col", "room idx"]]
        return i, j, k, self.rooms[k].array

    def swap(self, idx0, idx1):
        i0, j0, r0, arr0 = self.get_coords(idx0)
        i1, j1, r1, arr1 = self.get_coords(idx1)
        # Swap dataframe entries
        self.students.loc[idx0, ["row", "col", "room idx"]] = \
              i1, j1, r1
        self.students.loc[idx1, ["row", "col", "room idx"]] = \
              i0, j0, r0
        # Swap labels in dictionaries
        arr0[i0, j0], arr1[i1, j1] = arr1[i1, j1], arr0[i0, j0]

    def plot(self, room_idx, mode='lr', verbose=False):
        """Return a 2D plot of site energies for the room
        self.rooms[room_idx]. If mode is `lr`, the long-range
        interaction is plotted. If mode is `sr`, the short-range
        interaction is plotted. `transpo

        Args:
            room_idx (int)
            mode (str, optional)

        """
        fig, ax = plt.subplots()
        room_obj = self.rooms[room_idx]
        room = room_obj.array
        # Erase empty markers used in optimisation
        room = np.where(room == room_obj._empty_marker, '', room)
        size = room.shape
        fig.set_size_inches([size[1], size[0]])
        energy = np.where(room_obj.allowed, 0.0, np.nan)
        for irow in range(size[0]):
            for icol in range(size[1]):
                l0 = self.PES.strip_ccode(room[irow, icol])
                if l0 == '':
                    continue
                for jrow in range(size[0]):
                    for jcol in range(size[1]):
                        l1 = self.PES.strip_ccode(room[jrow, jcol])
                        if l1 == '':
                            continue
                        if irow == jrow and icol == jcol:
                            continue
                        if mode == 'lr':
                            E = self.PES.lr_pairwise(l0, l1)
                            energy[irow, icol] += E
                        elif mode == 'sr':
                            E = self.PES.sr_pairwise(
                                l0, (irow, icol),
                                l1, (jrow, jcol))
                            energy[irow, icol] += E
                        else:
                            raise RuntimeError
                        if E > 0 and verbose:
                            print(f'{room[irow, icol]}, {room[jrow, jcol]}, {E} ')
        if mode == 'lr':
            vmin = 0
            vmax = self.PES.a0
        elif mode == 'sr':
            vmin = 0
            vmax = np.max(self.PES.b)

        ax.matshow(energy, aspect='equal',
                   cmap=plt.cm.Wistia,
                   vmin=vmin, vmax=vmax)
        
        for i in range(size[0]):
            for j in range(size[1]):
                c = room[i,j]
                ax.text(j, i, str(c), va='center', ha='center')
        
        return fig, ax