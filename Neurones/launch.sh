#!/bin/bash
# lance plusieurs entrainements successifs

for i in `seq 0 1 2 3 4 5`;
do
    echo "simulation $i"
    ./occupation.py
done
mkdir assets
mv *.png assets/
mv *.h5 assets/
