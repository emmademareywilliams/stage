import tkinter as tk

from PyFina import getMeta, PyFina
import matplotlib.pylab as plt
import matplotlib
import datetime
import time
from dateutil import tz

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

LOCTZ = tz.gettz('Europe/Paris')
dir = "/home/ludivine/github/stage/CMB/Data/phpfina"

# premier point = créer un graphe matplotlib comprenant des données PHPFina
# deuxième point = faire afficher un graphe de données PHPFina dans une fenêtre tkinter
# troisième point = créer le graphe de fonctionnement de la pompe vierge
# quatrième point = avec l'interface tkinter, modifier (au pif) les données de fonctionnement de la pompe + les enregistrer
# cinquième pont = mettre plusieurs graphes (pompe + températures) dans une même fenêtre tkinter pour enfin
#                   pouvoir modifier les valeurs de fonctionnement de la pompe qui vont bien



def secondToHumanTime(sec, fmt="%m-%d \n %H: %M: %z", tz=LOCTZ):
    """
    equivalent between number of seconds and date readable by a human

    sec: unix number giving the starting time of the experiment
    tz: time zone object
    returns the corresponding date (format dd/ mm/ yyyy  h: m: s)
    """
    return datetime.date.fromtimestamp(sec).strftime(fmt)



######################## PREMIER POINT #########################

# on récupère les données du fichier meta sous forme affichable

def graphPyfina(feednb, frame):
    """
    creates the matplotlib graph representing the data corresponding to the feed number

    feednb: int that is the flux number we want to get on the graph
    frame: object tk.Frame aka frame in which the graphs are going to be printed
    """
    meta = getMeta(feednb,dir)
    # print(meta)
    step = 3600
    start = meta["start_time"]
    window = 10*24*3600  # duration of the plotting (here 1 week)
    length = meta["npoints"] * meta["interval"]  # time duration of the retrieved data
    if window > length:
        window = length
    nbpts = window // step
    data = PyFina(feednb, dir, start, step, nbpts)


######################## DEUXIÈME POINT #########################

# on affiche les données meta via une fenêtre tkinter
    f = matplotlib.pyplot.figure(figsize=(4,2), dpi=100)
    a = f.add_subplot(111)
    xrange = data.timescale()
    xhour = xrange /step
    xhuman = [secondToHumanTime(x + start) for x in xrange]
    #plt.subplot(111)
    if feednb == 42:
        plt.ylabel("pump operation")
        plt.ylim(0,2)
    else:
        plt.ylabel("temperature")
    plt.xlabel("time (time step = {} s)".format(step))
    plt.xticks(xrange, xhuman, rotation=90, fontsize=5)
    a.xaxis.set_major_locator(plt.MaxNLocator(10))
    a.plot(xrange, data)
    # pb: if we plot (xhuman, temp), we only get values of the temperature corresponding to the given dates
    # I should be able to plot (xrange, temp) BUT print xhuman for the x axis scale

    canvas = FigureCanvasTkAgg(f, root)
    canvas.draw()
    if feednb == 42:
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    # fill means the figure will fill the whole space of the window
    # expand means that the figure will adapt itself to the format of the canvas if the user changes its shape
    else:
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas._tkcanvas.pack(fill=tk.BOTH, expand=True)

def getStart(feednb):
    meta = getMeta(feednb,dir)
    start = meta["start_time"]
    return start

# on crée la fenêtre tkinter qui accueillera le graphe des données meta :
root = tk.Tk()
root.title("visualisation")
root.geometry("1900x1000")
frame = tk.Frame(root)

start = getStart(22)
localstart = datetime.datetime.fromtimestamp(start)
utcstart = datetime.datetime.utcfromtimestamp(start)
title = tk.Label(root, text="starting on :\nUTC {}\n{} {}".format(utcstart, time.tzname[0], localstart))
title.pack()

graphPyfina(11, frame)
graphPyfina(42, frame)

def quitter():
    root.quit()     # stops mainloop
    root.destroy()

canvas2 = tk.Frame(root, bg ='white', bd =2, relief = tk.GROOVE)
canvas2.pack(side = tk.RIGHT, padx =5, fill=tk.BOTH)
texte1 = tk.Label(canvas2, bg='white', text="Pump not in operation from: ")
texte1.grid(column=0, row=0)
# 'grid' permet de mettre plusieurs widgets sur la même ligne

day = tk.Entry(canvas2)
day.grid(column=1, row=0)
month = tk.Entry(canvas2)
month.grid(column=2, row=0)

# ce serait quand même plus ergonomique de faire un menu déroulant
#   --> dans ce cas, la liste des jours serait fonction de la date de départ que choisit l'utilisateur

texte2 = tk.Label(canvas2, bg='white', text="to:")
texte2.grid(column=0, row=1)

bouton = tk.Button(canvas2, text="quitter", command=quitter)
bouton.grid(column=1, row=2)

root.mainloop()
