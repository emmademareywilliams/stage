#!/bin/bash
# lance plusieurs entrainements successifs

for k in 0.5 0.6 1;
do
    for i in 1 2 3
    do
      echo "simulation k=$k stage $i"
      python3 retrain.py --N=700 --k=$k
    done
done
mkdir assets
mv *.png assets/
mv *.h5 assets/
mv *.csv assets/
