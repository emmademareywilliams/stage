# Pilotage des systèmes par un réseau neuronal

On souhaite piloter les installations énergétiques (pour le moment, le chauffage) d'un bâtiment via un système d'apprentissage renforcé. 


### Principes de l'apprentissage renforcé 

L'**apprentissage par renforcement** est une branche de l'intelligence artificielle qui "*consiste, pour un agent autonome (robot, etc.), à apprendre les actions à prendre, à partir d'expériences, de façon à optimiser une récompense quantitative au cours du temps*" (source [Wikipédia](https://fr.wikipedia.org/wiki/Apprentissage_par_renforcement)). 

Dans une telle situation d'apprentissage, on rencontre les éléments suivants :
* l'*agent* prend les décisions, c'est-à-dire qu'il choisit quelle action effectuer aux vues de son environnement ;
* l'*environnement* produit des états et des récompenses, quantités sur lesquelles s'appuie l'agent pour déterminer la politique à suivre (ensemble des actions choisies par l'agent et qui maximise l'apport en récompense). 

![RL principe](imagesHysteresis/RL.jpg)


Dans notre cas, l'agent est représenté par un réseau de neurones (géré par la bibliothèque Python *TensorFlow*).

Plus précisemment, la méthode qui va être utilisée est la méthode du *Q-learning* (...)


### Première étape : hystérésis 

Soit *Tc* la température de consigne. On souhaite que la température intérieure reste comprise entre *Tc + hh* et *Tc - hh* avec *hh* intervalle de confort autour de la température de consigne. On prendra le plus souvent *Tc = 20 °C* et *hh = 1 °C*. 

Pour que la température intérieure reste dans la zone de confort définie, le système de chauffage va devoir effectuer une hystérésis : 
* le chauffage se met en marche lorsque *Tint* atteint 19°C ; 
* le système est à l'arrêt dès que *Tint* vaut 21°C. 

On obtient la courbe caractéristique suivante :

![hysteresis](imagesHysteresis/hysteresis.png)

L'objectif, dans un premier temps, consiste à ce que l'agent reproduise ce comportement d'hysteresis. Le code permettant un tel fonctionnement correspond au fichier `hysteresisToolbox.py`.


### Deuxième étape : prise en compte de l'occupation

L'algorithme précédant nous a permis d'obtenir un comportement d'hystérésis *quel que soit l'occupation effective du bâtiment*. Or, afin d'en optimiser la consommation énergétique, il est important de prendre en compte son occupation, en d'autres termes, de considérer les moments durant lesquels des personnes sont présentes dans la structure. En dehors de ces heures d'occupation, il n'est pas nécessaire de maintenir la température de consigne.

Désormais, notre objectif est de maintenir la température dans la zone de confort *seulement lorsque le bâtiment est occupé*. Dans le cas contraire, pendant le weekend notamment, aucune consigne de température n'est appliquée. 

Pour mettre en place un tel algorithme, on considère une nouvelle variable appelée **time of flight** et qui correspond à la durée jusqu'à la prochaine période d'occupation. 


