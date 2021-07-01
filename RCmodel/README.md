# RCmodel

On peut modéliser simplement un bâtiment via un modèle RC : selon cette analogie électrique, on peut représenter son comportement dynamique avec une résistance et une capacité. 

![images](RCmodel.svg "modélisation RC bâtiment")

Si on étudie physiquement le comportement du bâtiment, on aboutit à l'équation différentielle suivante : 

![images](equadiff_solution.png "solution équation diff")

On peut donc modéliser l'évolution de la température interne par la fonction f(x). 

POur obtenir une estimation des valeurs de R et de C, on utilise le code `convo.py` 

