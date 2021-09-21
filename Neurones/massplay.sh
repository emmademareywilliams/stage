#!/bin/bash
# crée les graphes de synthèse pour tous les agents d'un directory

for f in assets/*.h5
    do
        echo $f
        ./play.py --mode=occupation --silent=True --tc=20 --n=900 --agent_name=$f
    done
