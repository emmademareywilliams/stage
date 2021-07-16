
# Interface tkinter pour le traitement des données 

Dans ce dossier, on trouvera les fchiers Python permettant de mettre à jour le flux de fonctionnement de la pompe. Pour ce faire, on fait afficher une fenêtre tkinter dans laquelle on rentre les dates de modification du fonctionnement de la pompe. 
* `interfacePump.py` est le fichier principal, qui permet :
   * l'affichage des graphes de températures et de fonctionnement de la pompe 
   * de choisir sur quel laps de temps la pompe ne fonctionne pas, et ce aux vues des données de température 
   * de mettre à jour le fichier .dat du fonctionnement de la pompe en fonction de ces nouvelles entrées
* `steps.py` et `test.py` sont des fichiers tests contenant les premières versions de certaines parties du code final
* `test_PyFina.py` permet de récupérer et d'afficher les données PHPFina : c'est ce code qui est à la base du fichier `interfacePump.py`
* `tkinter_test.py` est un fichier test de la bibliiothèque tkinter, dans lequel on peut retrouver un certain nombre des fonctionnalités de base de cette librairie


#### Sources :

* [Tutoriel](https://youtu.be/Zw6M-BnAPP0) pour utiliser Matplotlib et les fonctionnalités Tkinter 
* [Page Wikibooks](https://fr.wikibooks.org/wiki/Programmation_Python/Tkinter) qui décrit les principes de base de Tkinter
* [Page Wikibooks](https://fr.wikibooks.org/wiki/Programmation_Python/Et_pour_quelques_widgets_de_plus...) qui explicite des fonctionnalités Tkinter plus avancées (notamment au nveau des widgets)


