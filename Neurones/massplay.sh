#!/bin/bash
# crée les graphes de synthèse pour tous les agents d'un directory

dir="assets"

for f in "$dir/*.h5"
    do
        ./play.py --mode=occupation --silent=True --tc=20 --n=900 --name=$f
    done
