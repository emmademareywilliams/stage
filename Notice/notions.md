# Notions sur l'internet des objets 

Ici, une liste non exhaustive des sources et notions nécessaires à une compréhension plus poussée du fonctionnement 
de l'internet des objets.

## Définition sommaire 

Selon l'Union Internationale des Télécommunications, l'Internet des objets est une "*infrastructure mondiale pour la société 
de l'information, qui permet de disposer de services évolués en interconnectant des objets (physiques ou virtuels) grâce 
aux technologies de l'information et de la communication interopérables existantes ou en évolution*". 

Tout objet en capacité de se connecter à Internet est appelé *objet connecté* 

## HTTP, HTTPS et SSH

Dans l'écriture d'une adresse IP, on peut se retrouver confronté à ces différents cas de figure : 
* `http` : permet le simple transfert de données du serveur Internet à l'utilisateur, que ce soit dans un sens ou dans l'autre. Le principal problème de ce genre d'adresse est l'absence de toute sécurité : lorsque les données sont envoyées d'un serveur à l'autre, toute personne extérieure à l'échange peut s'y connecter et ainsi avoir accès au contenu. 
* `https`: le 's' veut dire 'sécurité', et c'est là tout l'intérêt de ce type d'adresse par rapport aux adresse http. Ici, le transfert est sécurisé de part en part car les données sont cryptées tout au long de l'échange grâce à une clé de chiffrement connue des seuls serveurs mis en relation. 

Le protocole *SSH* (Secure SHell) correspond justement à ce processus de cryptage des données qui permet de sécuriser les échanges via Internet. 
