#!/bin/bash -e

# Initial and final values of 1/kB*T
bi=0.05
bf=7.0

# Number of MC steps
n=50000

idum=17206

icholocator.py -bi ${bi} -bf ${bf} -n ${n} -i ${idum} --pes params.json --students ../students.csv \
    --rooms ../../data/theory_floorplans/HIL_{061_half,061_half,061_half,061_half,075,075}.csv \
    --labels F61_top F61_bottom G61_top G61_bottom F75 G75 \
    --name residuals.pdf
