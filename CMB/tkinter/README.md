Sources :

* [Tutoriel](https://youtu.be/Zw6M-BnAPP0) pour utiliser Matplotlib et les fonctionnalités Tkinter 
* [Page Wikibooks](https://fr.wikibooks.org/wiki/Programmation_Python/Tkinter) qui décrit les principes de base de Tkinter
* [Page Wikibooks](https://fr.wikibooks.org/wiki/Programmation_Python/Et_pour_quelques_widgets_de_plus...) qui explicite des fonctionnalités Tkinter plus avancées (notamment au nveau des widgets)


À améliorer : 
* l'instruction `window.mainloop()` continue de s'exécuter même quand on appuie sur le bouton *Quitter* dans la fenêtre ; il faut alors faire un *Ctrl+C* afin de terminer l'exécution... *--> il faudrait que la boucle se termine toute seule*
    **--> problème réglé via l'instruction `quit`** 
* avec le mode `NavigationToolbar`, quand j'appuie sur les commandes, la fenêtre se fige et il n'est plus possible d'appuyer sur aucun bouton... Il faut faire un *Ctrl+C* (et attendre un certain moment) que la fenêtre puisse se fermer
    **--> on dirait que c'est le bouton "pan/zoom" qui pose problème...**
