#!/bin/bash

toLink=("icho2023/seating/icholocator.py")
toLink+=("icho2023/seating/assign_codes.py")

for f in ${toLink[@]}; do
    ln -s -f -t bin "$( pwd )/$f"
done
