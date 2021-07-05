# Correspondance entre les numéros de flux et les mesures des capteurs 

## Numéros des fichiers .dat et .meta

C.f. cette [page](https://alexandrecuer.github.io/smartgrid/bloch.html) pour plus de détails sur les flux. Ici ne seront relevés que les numéros de flux utiles pour la suite - en d'autres termes, les températures extérieures, intérieures et des circuits d'eau.  

Numéro du flux | Grandeur mesurée | Unité
--|--|--
5 | Température extérieure | °C
8 | Température intérieure salle de musique Nord | °C
11 | Température intérieure salle de technologie Nord | °C
14 | Température intérieure salle de cours Sud | °C
17 | Température intérieure salle d’art plastique Sud | °C
**Circuits d'eau**
19 | Température de départ circuit Sud | °C
20 | Température de retour circuit Sud | °C
21 | Température de départ circuit Nord | °C
22 | Température de retour circuit Nord | °C


## Sur Emoncms 

> Dans la plupart des cas, les flux d'Emoncms ne correspondent pas aux numéros des fichiers PHPFina associés (en effet, le numéro des flux sur le site est fonction de l'ordre d'ajour des noeuds sur Emoncms). 

Numéro du flux | Grandeur mesurée | Tag
--|--|--
6 | Température de départ circuit Sud | PT100_1_depSUD
7 | Température de retour circuit Sud | PT100_2_retSUD
10 | Température de départ circuit Nord | PT100_3_depNORD
11 | Température de retour circuit Nord | PT100_4_retNORD
8 | Température intérieure Sud | tempB216SUD
9 | Température extérieure | temp 


