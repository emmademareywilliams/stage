import tkinter as tk

Fenetre = tk.Tk()
Fenetre.title("Ceci est une fenêtre")

#widget Button
bouton = tk.Button(Fenetre, text="quitter", command=Fenetre.destroy)  # bouton qui détruit la fenêtre
bouton.pack()  # insère le bouton dans la fenêtre

# widget Label
texte = tk.Label(Fenetre, text="Hello world")
texte['fg'] = 'black'  # texte de couleur noire
texte['bg'] = 'blue'  # pour changer la couleur du fond
texte.pack()

# widget Entry
entree = tk.Entry(Fenetre)
entree.pack()

# formulaire avec Entry :
def repondre():
    affichage['text'] = reponse.get()  # lecture du conteu du widget "reponse"

nom = tk.Label(Fenetre, text='Entrez votre nom :')
reponse = tk.Entry(Fenetre)
valeur = tk.Button(Fenetre, text="valider", command=repondre)
affichage = tk.Label(Fenetre, width=30)
votre_nom = tk.Label(Fenetre, text='est votre nom')

nom.pack()
reponse.pack()
valeur.pack()
affichage.pack()
votre_nom.pack()   # les widgets apparaissent dans l'ordre où on les déclare

Fenetre.mainloop()

# widget Canvas
newF = tk.Tk()
newF.title("fenêtre de dessin")
zone_dessin = tk.Canvas(newF, width=500, height=500, relief='ridge')  # définit les dimensions du canevas
zone_dessin.pack()
zone_dessin.create_line(0,0,500,500)  # crée une ligne diagonale
zone_dessin.create_rectangle(100,100,200,200)  # crée un rectangle
bouton_sortir = tk.Button(newF, text='Quitter', command=newF.destroy)
bouton_sortir.pack()

newF.mainloop()


# widget Radio

class RadioDemo(tk.Frame):
    """Démo : utilisation de widgets 'boutons radio'"""
    def __init__(self, boss =None):
        """Création d'un champ d'entrée avec 4 boutons radio"""
        tk.Frame.__init__(self)
        self.pack()
        # Champ d'entrée contenant un petit texte :
        self.texte = tk.Entry(self, width =30, font ="Arial 14")
        self.texte.insert(tk.END, "La programmation, c'est génial")
        self.texte.pack(padx =8, pady =8)
        # Nom français et nom technique des quatre styles de police :
        stylePoliceFr =["Normal", "Gras", "Italique", "Gras/Italique"]
        stylePoliceTk =["normal", "bold", "italic"  , "bold italic"]
        # Le style actuel est mémorisé dans un 'objet-variable' Tkinter ;
        self.choixPolice = tk.StringVar()
        self.choixPolice.set(stylePoliceTk[0])
        # Création des quatre 'boutons radio' :
        for n in range(4):
            bout = tk.Radiobutton(self,
                               text = stylePoliceFr[n],
                               variable = self.choixPolice,
                               value = stylePoliceTk[n],
                               command = self.changePolice)
            bout.pack(side=tk.LEFT, padx=5)
        quitter = tk.Button(self, text='quitter', command=self.destroy)
        quitter.pack()

    def changePolice(self):
        """Remplacement du style de la police actuelle"""
        police = "Arial 15 " + self.choixPolice.get()
        self.texte.configure(font=police)

if __name__ == '__main__':
    RadioDemo().mainloop()
