# Résultats obtenus pour le modèle RC sur le collège Marc Bloch 

Tous les tests ont été effectués sur la base des données du bâtiment Nord (pour la température intérieure ainsi que les températures de départ 
et de retour du circuit d'eau).

### Durée de la simulation : 10 jours 

Pour tous les résultats ci-dessous, on a pris :
* une capacité calorifique de l'eau de *1162.5 Wh/m3/K* ;
* une fenêtre de *10 jours* ; 
* un débit de *5 m3/h* ; 
* un delta T (entre les température de départ et d'arrivée) de *10*. 

Date de début | R | C | Poids 
---|---|---|---
20/02 | 2.64850632e-04 | 3.99920238e+08 | [1e-5, 1e8]
27/02 | 2.99444995e-04 | 7.57208244e+08 | [1e-5, 1e8]
05/03 | 3.42506838e-04 | 1.06209090e+09 | [1e-5, **1e9**]
18/03 | 3.14307842e-04 | 5.15186005e+08 | [1e-5, 1e8]
05/04 | 2.47025473e-04 | 1.09630532e+09 | [1e-5, 1e8]

**Observations pour cette fenêtre** :
* si la fenêtre correspond uniquement à une période de vacances, la température simulée sera toujours constante (cf. figure ci-dessous). En effet, l'absence des variations caractéristiques pour la température de départ en semaine ne permet pas d'obtenir une convolution satisfaisante. 

![12 février](12_02_10days.png)

* À certaines dates (c'est notamment le cas de la première moitié de mars), il a fallu changer les paramètres des poids afin que l'exponentielle contenue dans le calcul de la convolution ne tende pas vers l'infini. 


### Durée de la simulation : 20 jours 

On augmente le temps de la simulation à 20 jours, toutes choses égales par ailleurs. On pourra mettre à jour la valeur des poids au besoin. 

Date de début | R | C | Poids 
---|---|---|---
20/02 | 3.08814171e-04 | 8.63446560e+08 | [1e-5, 1e8]
04/03 | 3.19412465e-04 | 8.87378799e+08 | [1e-5, **1e9**]
29/03 | 1.37565505e-05 | 1.08216951e+11 | [1e-5, 1e8]




