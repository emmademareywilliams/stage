# Stage CEREMA Clermont-Ferrand - été 2021 

Dans ce répertoire, on pourra trouver tout ce qui a pu être effectué lors de mon stage au laboratoire du CEREMA - Clermont-Ferrand entre juin et septembre 2021. 

* `CMB` : répertoire dédié à l'étude de cas du Collège Marc Bloch. Le bâtiment a été instrumenté par le CEREMA début 2021 dans le cadre d'une mission pour le CD63 via le système Themis. Dans ce dossier se trouvent :
  * les codes pour modifier l'interface graphique Emoncms afin de mettre à jour manuellement le flux de la pompe (non monitorée lors de l'instrumentation) ;
  * les résultats de la modélisation RC qui a suivi.

* `MountainCarPB` : le problème classique de la montagne est une première approche vis-à-vis de l'apprentissage par renforcement et des réseaux de neurones
* `Neurones` : dossier contenant tout ce qui a trait à l'apprentissage renforcé et à ses différents cas d'utilisation (hystérésis classique ou couplée avec des périodes de non occupation) 
* `Notice` : dossier contenant la majorité de la documentation générale sur le sujet du stage, notamment : 
  * la notice d'utilisation du système Themis ;
  * une liste des lignes de commandes couramment utilisées sous Linus ; 
  * une présentation de certaines notions nécessaires à la compréhension de certains aspects du sujet ;
  * quelques bases du langage PHP. 

* `RCmodel` : contient tous les fichiers nécessaires à la modélisation thermique d'un bâtiment via une analogie RC, sur la base de données physiques mesurées (principalement des données de température) 
* `THEMISoffice` : on y trouvera les codes relatifs au capteur MBUS de Themis, qui effectue les opérations suivantes : 
  * réception des signeux radios en provenance des capteurs ; 
  * décodage de ces signaux si le capteur qui les a émis est de type Enless ; 
  * filtrage des signaux en fonction du numéro de série du capteur ; 
  * envoi des données décodées sur Emoncms. 

