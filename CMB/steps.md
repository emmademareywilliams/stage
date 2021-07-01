# Travail sur les données du Collège Marc Bloch 

Les données récoltées au collège Marc Bloch consistent essentiellement en les températures intérieures et extérieures dans les différentes zones du bâtiment. Or, aucun capteur
n'a été installé qui puisse mesurer le fonctionnement de la pompe. Cependant, on peut déduire, à partir des données de température, à quels moments le chauffage est activé ou non :
il va donc s'agir de créer manuellement un flux pour le fonctionnement de la pompe, puis de le modifier afin qu'il corresponde au comportement réel du chauffage. 

Pour ce faire, il faudra paramétrer l'interface Emoncms afin de créer une nouvelle visualisation et de modifier les données directement sur le site. 


## Au préalable 

Pour accéder à l'UI du routeur à distance : 
```
https://chaufferiedlcf.ddns.net 
```

## Step 1 : créer le flux 

Pour créer le flux qui correspondra au fonctionnement de la pompe, on doit créer deux fichiers : 
* un fichier `.meta` : on copiera le meta de la température de départ du circuit d'eau ;
* un fichier `.dat` : il sera initialisé via Python pour ne contenir que des 1. Ce sera ce fichier qui par la suite sera modifié pour correspondre au comportement de la pompe. 

POur écrire les données dans le fichier `.dat`, on utilisera la bibliothèque `struct` dans Python (voir [ici](https://docs.python.org/3/library/struct.html) la documentation de la librairie). 
