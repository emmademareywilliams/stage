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

Le protocole **SSH** (Secure SHell) correspond justement à ce processus de cryptage des données qui permet de sécuriser les échanges via Internet. 

## Protocoles RS485 et RS232

**RS232** et **RS485** sont deux protocoles standardisés relatifs à la communication et au transfert de la donnée. Ils permettent tous deux la communication en série entre l'ordinateur et ses périphériques et sont largement utilisés dans l'industrie. Les différences entre les deux protocoles sont résumées dans le tableau ci-dessous : 

Critère | RS232 | RS485
--|--|--
Nombre de fils | 9 à 25 | 2 (transmission + GND)
Transmission | Bidirectionnelle | Unidirectionnelle 
Longueur | 15 m | 1200 m 

Ces différences impliquent une utilisation différente pour chacun des deux protocoles, même si ceux-ci peuvent être utilisés de manière simultanés sur un même appareil. 


## Le modèle TCP/IP 

Le modèle **TCP/IP** est une suite de protocole relatif au transport des données. Il correspond à l'ensemble des règles de communication sur Internet et se base sur la notion d'adressage IP, c'est-à-dire le fait de fournir une adresse IP à chaque machine du réseau afin de pouvoir acheminer des paquets de données. 

Le modèle est composé de plusieurs couches : 
* Le protocole *TCP* (Transmission Control Protocol) correspond à la couche transport qui prend en compte les données en provenance (ou en direction) de la couche IP ;
* Le protocole *IP* (Internet Protocol) est la couche Internet qui gère l'élaboration et le transport des paquets de données (ou datagrammes) IP. 

Le modèle permet ainsi de connecter un appareil à une adresse IP spécifique et d'établir un transfert de données, dans un sens ou dans l'autre, entre les deux serveurs. 


## MQTT 

Le protocole **MQTT** est un protocole de communication très utile lorsque l'on traite de l'Internet des objets. En effet, il s'agit d'un protocole open source de messagerie qui assure des communications non permanentes entre des appareils par le transport de leurs messages. Il est particulièrement intéressant du fait de sa légéreté, qui le rend compatible avec des équipements munis de petits microcontrôleurs. 



