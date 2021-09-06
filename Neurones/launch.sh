#!/bin/bash
# lance plusieurs entrainements successifs

for i in 1 2;
do
    echo "simulation $i"
    python3 trainOcc.py
done
mkdir assets
mv *.png assets/
mv *.h5 assets/
