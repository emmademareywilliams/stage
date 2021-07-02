# Travail sur les données du Collège Marc Bloch 

Les données récoltées au collège Marc Bloch consistent essentiellement en les températures intérieures et extérieures, ainsi que des températures de chauffe, dans les différentes zones du bâtiment. Or, aucun capteur
n'a été installé qui puisse mesurer le fonctionnement de la pompe. Cependant, on peut déduire, à partir des données de température, à quels moments le chauffage est activé ou non :
il va donc s'agir de créer manuellement un flux pour le fonctionnement de la pompe, puis de le modifier afin qu'il corresponde au comportement réel du chauffage. 

Pour ce faire, il faudra paramétrer l'interface Emoncms afin de créer une nouvelle visualisation et de modifier les données directement sur le site. 


## Au préalable 

Pour accéder à l'UI du routeur à distance : 
```
https://chaufferiedlcf.ddns.net 
  OU
176.178.161.180

User : root
Password : Taxo10in2xcw*
```

Au besoin, on pourra ouvrir une connexion *ssh* dans l'onglet *Nat* de l'UI du routeur. 


## Step 1 : créer le flux 

Pour créer le flux qui correspondra au fonctionnement de la pompe, on doit créer deux fichiers : 
* un fichier `.meta` : on copiera le meta de la température de départ du circuit d'eau ;
* un fichier `.dat` : il sera initialisé via Python pour ne contenir que des 1. Ce sera ce fichier qui par la suite sera modifié pour correspondre au comportement de la pompe. 

Pour écrire les données dans le fichier `.dat`, on utilisera la bibliothèque `struct` dans Python (voir [ici](https://docs.python.org/3/library/struct.html) la documentation de la librairie). 
On s'inspirera des fonctions `createMeta`, `createFeed` et `newPHPFina` disponible à [ce lien](https://github.com/alexandrecuer/tf_works/blob/master/BIOS/src/tools/phpfina.py). Ces fonctions permettent de créer un nouvel objet PHPFina, non relié à un flux Emoncms, en utilisant un tableau numpy. 


## Step 2 : faire reconnaître le flux par Emoncms 

Emoncms reconnaît des flux FINA associés à des métadonnées SQL : aussi, il faudra associer notre flux créé de toutes pièces à de telles métadonnées afin qu'il soit reconnu par Emoncms et apparaisse dans la liste des flux. 

Pour installer mysql pour python : 

```
sudo apt-get install -y python3-mysql.connector
```

Dans un script python, on commence par importer un connecteur :

```
import mysql.connector
```
> C.f fichier `mysql_test.py`


## Step 3 : visualiser le nouveau flux dans un graphe Emoncms
  
Les fichiers qui gèrent l'interface graphique d'Emoncms se trouvent [ici](https://github.com/emoncms/emoncms/tree/master/Modules/vis) (ou bien, sur la machine, au chemin suivant : `opt/openenergymonitor/emoncms/Modules/vis`).

On dupliquera le fichier `EditRealtime.php` pour ne pas casser cette visualisation : le nouveau fichier, appelé `EditRealtime2.php`, permettra la création du graphe où seront superposées les courbes de température et de fonctionnement de la pompe. 

Il faudra ensuite faire afficher `EditRealtime2` dans le menu déroulant de l'onglet visualisation d'Emoncms. 

