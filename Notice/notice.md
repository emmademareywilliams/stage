# Notice d'utilisation du système THEMIS 

Le système *THEMIS* (...) 

## Présentation du système 


## Installations préalables 

La programmation est faite en Python : on s'assurera dans un premier temps que Python est bien installé sur l'ordinateur qui sera utilisé pour manipuler les données. À défaut, 
on peut l'installer en suivant [ce lien](https://www.python.org/downloads/) (pour Windows et Mac). À noter que Python est installé par défaut sur les appareils Linux. 

Avant de continuer, il est toujours intéressant de vérifier que le système est à jour. Pour obtenir la version de Python qui tourne sur la machine, on entrera la ligne de commande suivante dans le terminal : 
```
python3 --version
```

2 types de données : 
* Les données récoltées par THEMIS sont de type *emoncms PHPFINA* ;
* Les données prises en charge par le système sont de type *PyFina* (une sous-classe de numpy np.ndarray) : elles permettent d'importer dans Python les données récoltées. 

Pour manipuler ces données, il va falloir installer un certain nombre de packages Python. Pour ce faire, il faut ouvrir le terminal de l'ordinateur et y taper la ligne de 
commande suivante : 
* sur MacOS et Linux : 
```
python3 -m install PyFina 
```

* sur Windows : 
```
py -m pip install PyFina
```
On pourra tester ce nouveau package en suivant les instructions disponibles à [cette adresse](https://github.com/Open-Building-Management/PyFina/blob/main/README.md). 


## Manipulation des données 

### Manipulation directe des données Emoncms 

Pour accéder directement aux relevés des différentes données, on entre l'adresse suivante dans la barre de recherche d'un navigateur: 
INSÉRÉR ADRESSE IP  

On se retrouve alors avec un certain nombre d'onglets sur la gauche de l'écran : 

![lib](onglets.png "Figure - onglets disponibles")

* *Inputs* correspond aux entrées du système (les différents capteurs et les grandeurs qu'ils mesurent) ;
* *Feeds* correspond aux données relevées, qui sont du type Emoncms PHPFINA ; 
* *Graphs* permet d'afficher l'évolution temporelle des grandeurs à différentes échelles et de construire certains graphes selon les besoins et objectifs de l'utilisateur ;
* *Visualisation* permet entre autre de visualiser les graphes de confort (graphiques psychrométriques). 


### Importation des données Emoncms sous Python 

```
wget https://raw.githubusercontent.com/alexandrecuer/smartgrid/master/datasets/emoncms-backup-2020-04-22.tar.gz
tar -xvf emoncms-backup-2020-04-22.tar.gz
# seulement un exemple, l'adresse ne sera pas celle-ci 
```

Il est possible que wget ne soit pas encore installé sur votre machine. Dans ce cas, il faudra procéder à son installation (pour [Windows](https://builtvisible.com/download-your-website-with-wget/) ou [Mac](https://www.maketecheasier.com/install-wget-mac/)). 

Une fois la tâche effectuée, vous pourrez retrouver le dossier contenant les données PyFina.


