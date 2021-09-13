"""
pour révisualiser les indicateurs qualité des entrainements à partir du csv enregistré
permet d'afficher les timestamps lorsque la souris survole le graphique du haut
"""

import readline
import numpy as np
import os
import glob
import matplotlib.pyplot as plt

def simplePathCompleter(text,state):
    """
    tab completer pour les noms de fichiers, chemins....
    """
    line   = readline.get_line_buffer().split()

    return [x for x in glob.glob(text+'*')][state]

readline.set_completer_delims('\t')
readline.parse_and_bind("tab: complete")
readline.set_completer(simplePathCompleter)
name = input("nom du fichiers de stats ?")


def update_annot(ind):
    """
    affiche le timestamp de l'épisode dans l'annotation et la positionne au bon endroit
    """
    pos = sc[-1].get_offsets()[ind["ind"][0]]
    #print(pos)
    annot.xy = pos
    text = "épisode {}\n ts={}\n Tintoccmoy={:.2f}".format(int(pos[0]),int(stats[int(pos[0]),0]),stats[int(pos[0]),9])
    annot.set_text(text)

def hover(event):
    """
    rend visible une annotation lorsque la souris passe sur une valeur de Tintocc moyenne
    la rend invisible lorsque la souris s'éloigne
    """
    vis = annot.get_visible()
    if event.inaxes == ax1:
        cont, ind = sc[-1].contains(event)
        if cont:
            update_annot(ind)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

if os.path.isfile(name):

    stats = np.loadtxt(name, skiprows=1, delimiter=',')

    fig = plt.figure(figsize=(20, 10))
    ax1 = plt.subplot(211)
    plt.title(name)
    # scatter plots
    sc = []
    colors = ["blue", "orange", "green"]
    for i in range(9):
        j = i // 3
        if i % 3 == 1:
            sc.append(plt.scatter(np.arange(stats.shape[0]),stats[:,i+2],c=colors[j]))
            #plt.plot(stats[:,i+2], "o", color=colors[j])
        else :
            plt.plot(stats[:,i+2], color=colors[j])
    annot = ax1.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)
    # affichage des récompenses
    plt.subplot(212, sharex = ax1)
    plt.plot(stats[:,1])
    fig.canvas.mpl_connect("motion_notify_event", hover)
    plt.show()

    from dataengines import getMeta
    dir = "/var/opt/emoncms/phpfina"
    meta = getMeta(1, dir)
    _tss = meta["start_time"]
    fullLength = meta["npoints"] * meta["interval"]
    _tse = meta["start_time"]+fullLength
    xr = np.arange(_tss, _tse, 3600)
    table= np.zeros(xr.shape[0])
    for ts in stats[:,0]:
        i = (int(ts) - _tss) // 3600
        table[i] += 1
    plt.figure(figsize=(20, 10))
    plt.subplot(111)
    plt.title("{}\n répartition des entrainements".format(name))
    plt.plot(xr,table)
    plt.show()
