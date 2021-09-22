#!/bin/bash
# fait jouer un réseau donné pour plusieurs valeurs de (R,C)

f=entrainement_a_la_chaine/k0dot5_3/*.h5
list=("3.08814171e-04" "5e-4" "1e-3")
C=8.63446560e+08

for val in ${list[@]}
    do 
        echo "on joue avec R=$val et C=$C"
        ./playwithRC.py --mode=occupation --silent=True --tc=20 --n=100 --agent_name=$f
    done 
