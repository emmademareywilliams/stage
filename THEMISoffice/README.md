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
