For step 2: 

https://youtu.be/Zw6M-BnAPP0 


À améliorer : 
* l'instruction `window.mainloop()` continue de s'exécuter même quand on appuie sur le bouton *Quitter* dans la fenêtre ; il faut alors faire un *Ctrl+C* afin de terminer l'exécution... *--> il faudrait que la boucle se termine toute seule*
    **--> problème réglé via l'instruction `quit`** 
* avec le mode `NavigationToolbar`, quand j'appuie sur les commandes, la fenêtre se fige et il n'est plus possible d'appuyer sur aucun bouton... Il faut faire un *Ctrl+C* (et attendre un certain moment) que la fenêtre puisse se fermer
