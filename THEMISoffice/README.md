# Notice du dossier 

Dans ce répertoire on trouvera tous les codes relatifs au fonctionnement du système THEMIS installé dans mon bureau :

* `router_mode.py` permet de lire sur l'ordinateur les données en provenance des capteurs et reçues par le récepteur MBus. On peut choisir le mode 
de connexion au routeur : en utilisant dans Python soit la bibliothèque `socket` soit la bibliothèque `serial`.
* `mqttTools.py` est le fichier qui prend en charge l'envoi des données sur le site Emoncms.  

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
