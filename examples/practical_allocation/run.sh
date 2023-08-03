#!/bin/bash -e

# Initial and final values of 1/kB*T
bi=0.05
bf=8.0

# Number of MC steps
n=10000

idum=17206

icholocator.py -bi ${bi} -bf ${bf} -n ${n} -i ${idum} --pes params.json --students ../students.csv \
    --rooms ../../data/practical_floorplans/{C191-3,C191-4,E374,E376,E392,E394,G_lab,G_lab,G_lab,J_lab,J_lab,J_lab,J_lab,J_lab}.csv \
    --labels C191_3 C191_4 E374 E376 E392 E394 G194 G196 G198 J190 J192 J194 J196 J198 \
    --name residuals.pdf
