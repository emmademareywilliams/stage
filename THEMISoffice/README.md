# Notice du dossier 

Dans ce répertoire on trouvera tous les codes relatifs au fonctionnement du système THEMIS installé dans mon bureau :

* `ota2tcp.py` est le fichier finalisé qui permet :
  - de choisir le mode de connexion au routeur : en utilisant dans Python soit la bibliothèque `socket` soit la bibliothèque `serial`
  - de lire sur l'ordinateur les données en provenance des capteurs et reçues par le récepteur MBus
  - d'écrire sur le port série du routeur lorsqu'un nouveau capteur lance une procédeure d'installation 
  - de filtrer les capteurs à partir de leur numéro de série afin de n'afficher sur Emoncms que les données qui nous intéressent 

* `router_mode.py` est une ancienne version de `ota2tcp.py` (elle ne permet notamment pas le filtrage des capteurs) 
* `mqttTools.py` est le fichier qui prend en charge l'envoi des données sur le site Emoncms  
* `makefile` est le fichier qui permet d'automatiser l'exécution du code `ota2tcp.py` en le paramétrant en service exécutable. 


## Interface Emoncms

Pour se connecter à Emoncms et visualiser les entrées (correspondant aux capteurs dont les données sont reçues par le récepteur MBus), on entrera l'adresse 
suivante dans la barre de recherche d'un navigateur : 

```
127.0.0.1/emoncms
```

> Il faudra être connecté localement au routeur pour avoir accès à Emoncms de cette manière. 

Il se peut que le service `emoncms_mqtt` ne soit pas actif (pour vérifier s'il l'est, se référer à l'onglet *Admin* dans Emoncms). Si le service n'est pas opérationnel, il faudra le rebooter avec la ligne de commande suivante : 
```
sudo systemctl restart emoncms_mqtt
```

L'adresse suivante donne accès à un *buffer*, c'est-à-dire à un tampon entre la machine de l'utilisateur et Emoncms : 
```
http://127.0.0.1/phpRedisAdmin
```
On pourra y trouver entre autres les dernières données reçues sous la forme d'une base de données SQL, ainsi qu'un système de queue lorsque les flux auront été établis (dans le cas où plusieurs signaux en provenance du même capteur sont reçus en même temps). 


## Makefile 

Le fichier `makefile` permet de paramétrer le fichier `ota2tcp.py` en tant que service exécutable. Il contient 2 méthodes :
* la méthode `install` qui installe le service, notamment en créant les fichiers log et conf, en les redirigeant vers les fichiers adéquates puis en démarrant l'exécution du système ;
* la méthode `uninstall` qui permet une désinstallation propre du service (les symlinks sont écrasés). 




