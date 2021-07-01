# Notions sur l'internet des objets 

Ici, une liste non exhaustive des sources et notions nécessaires à une compréhension plus poussée du fonctionnement 
de l'internet des objets.

## Définitions sommaires 

Selon l'Union Internationale des Télécommunications, l'**Internet des objets** est une "*infrastructure mondiale pour la société 
de l'information, qui permet de disposer de services évolués en interconnectant des objets (physiques ou virtuels) grâce 
aux technologies de l'information et de la communication interopérables existantes ou en évolution*". 

Tout objet en capacité de se connecter à Internet est appelé *objet connecté*. 

## HTTP, HTTPS et SSH

Dans l'écriture d'une adresse IP, on peut se retrouver confronté à ces différents cas de figure : 
* `http` : permet le simple transfert de données du serveur Internet à l'utilisateur, que ce soit dans un sens ou dans l'autre. Le principal problème de ce genre d'adresse est l'absence de toute sécurité : lorsque les données sont envoyées d'un serveur à l'autre, toute personne extérieure à l'échange peut s'y connecter et ainsi avoir accès au contenu. 
* `https`: le 's' veut dire 'sécurité', et c'est là tout l'intérêt de ce type d'adresse par rapport aux adresses http. Ici, le transfert est sécurisé de part en part car les données sont cryptées tout au long de l'échange grâce à une clé de chiffrement connue des seuls serveurs mis en relation. 

Le protocole **SSH** (Secure SHell) correspond au processus de cryptage des données qui permet de sécuriser les échanges via Internet. Il repose sur l'existance de deux clés de cryptage : 
* une clé *publique* à laquelle quiconque peut avoir accès et qui est utilisée pour crypter les données ;
* une clé *privée* connues des seuls client et serveur, qui permet le décryptage des informations. 

Chacun de ces protocoles correspond à un port différent : le port 80 pour `http`, le port 443 pour `https` et le port 22 pour `ssh`. 

## Protocoles RS485 et RS232

**RS232** et **RS485** sont deux protocoles standardisés relatifs à la communication et au transfert de la donnée. Ils permettent tous deux la communication en série entre l'ordinateur et ses périphériques et sont largement utilisés dans l'industrie. Les différences entre les deux protocoles sont résumées dans le tableau ci-dessous : 

Critère | RS232 | RS485
--|--|--
Nombre de fils | 9 à 25 | 2 (transmission + GND)
Transmission | Bidirectionnelle | Bidirectionnelle / unidirectionnelle (pour THEMIS)
Longueur | 15 m | 1200 m 

Ces différences impliquent une utilisation différente pour chacun des deux protocoles, même si ceux-ci peuvent être utilisés de manière simultanés sur un même appareil. 
En pratique, les deux protocoles se valent. 


## Le modèle TCP/IP 

Le modèle **TCP/IP** est une suite de protocole relatif au transport des données. Il correspond à l'ensemble des règles de communication sur Internet et se base sur la notion d'adressage IP, c'est-à-dire le fait de fournir une adresse IP à chaque machine du réseau afin de pouvoir acheminer des paquets de données. 

Le modèle est composé de plusieurs couches : 
* Le protocole *TCP* (Transmission Control Protocol) correspond à la couche transport qui prend en compte les données en provenance (ou en direction) de la couche IP ;
* Le protocole *IP* (Internet Protocol) est la couche Internet qui gère l'élaboration et le transport des paquets de données (ou datagrammes) IP. 

Le modèle permet ainsi de connecter un appareil à une adresse IP spécifique et d'établir un transfert de données, dans un sens ou dans l'autre, entre les deux serveurs. 


## MQTT 

Le protocole **MQTT** est un protocole de communication très utile lorsque l'on traite de l'Internet des objets. En effet, il s'agit d'un protocole open source de messagerie qui assure des communications non permanentes entre des appareils par le transport de leurs messages. Il est particulièrement intéressant du fait de sa légéreté, qui le rend compatible avec des équipements munis de petits microcontrôleurs. 


## Journalisation avec Python

Il est important de mettre en place un système de journalisation lorsque l'on développer un logiciel ou un service car il nous permet de suivre le déroulé des événements lors de leur fonctionnement. En Python, on utilisera la bibliothèque *logging* dont un tutoriel est disponible à [cette adresse](https://docs.python.org/fr/3/howto/logging.html). 

Les fonctions principales sont les suivantes :
* `logging.info()` ou `logging.debug()` pour rapporter des événements qui ont lieu lors du fonctionnement ;
* `logging.warning()` pour émettre un avertissement (sans que le fonctionnement du logiciel soit compromis) ;
* `logging.error()` ou `logging.critical()` pour rendre compte d'une erreur qui porte préjudice au bon fonctionnement du service. 

Ces fonctions sont associées aux différents niveaux d'importance attribués à un événement : 
```
DEBUG --> INFO --> WARNING --> ERROR --> CRITICAL 
```
> Par défaut, le niveau d'affichage dans le log est `WARNING`.

Communément, on crée un fichier `.log` qui enregistrera toutes les informations relatives au déroulement du fonctionnement du logiciel. Pour créer ce fichier, on utilisera la fonction suivante : 

```
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
```

L'utilisation de l'argument `level` permet de choisir le niveau seuil à partir duquel les informations seront affichées dans le log. 


## Requêtes synchrones et asynchrones 

Un code **synchrone** s'exécute ligne après ligne en attendant la fin de l'exécution de la ligne précédente : il ne peut donc y avoir de tâches effectuées en parallèle. 
Au contraire, dans un code **asynchrone**, la ligne suivante n'attendra pas que la ligne asynchrone ait fini son exécution.

Plus généralement, la communication de données peut être synchrone ou asynchrone : 
* Dans le cas d'une connexion *synchrone*, tous les interlocuteurs sont connectés au même moment et échangent les informations de manière simultanée et instantannée. 
* Si la communication est *asynchrone*, les échanges se font en mode différé et les interlocuteurs ne doivent pas tous être connectés au même moment. Cette méthode de communication repose sur le mécanisme de dépôt de l'information dans des réservoirs de stockage momentané publics ou privés.


## Sites statiques ou dynamiques 

Dans le monde de la programmation web, on rencontre deux types de sites : 

* les sites **statiques** apparaissent tels qu'ils on été conçus, c'est-à-dire que leur contenu ne change pas. Les principaux langages utilisés pour ce genre de site sont HTML5 et CSS3. Ils sont beaucoup plus simples et moins chers à développer.
* les sites **dynamiques** affichent un contenu et des informations différentes suivant l’interaction et les demandes des visiteurs. Ils résultent d'une combinaison entre un langage (de programmation, comme PHP ou de script, comme JavaScript) et d'une base de données (e.g. MySQL). 


Un **CMS** (Content Management System) est un logiciel permettant la création et la gestion d'un site web dynamique. Le plus utilisé à ce jour est WordPress. 

