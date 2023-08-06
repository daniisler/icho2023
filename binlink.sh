#!/bin/bash

toLink=("icho2023/seating/icholocator.py")
toLink+=("icho2023/seating/assign_codes.py")
toLink+=("icho2023/seating/lab_covers.py")

for f in ${toLink[@]}; do
    ln -s -f -t bin "$( pwd )/$f"
done
