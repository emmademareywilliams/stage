import datetime
import time
from dateutil import tz

LOCTZ = tz.gettz('Europe/Paris')


def secondToHumanTime(sec, start, fmt="%Y-%m-%d %H: %M :%S: %z", tz=LOCTZ):
    """
    equivalent between number of seconds and date readable by a human

    sec: number of seconds since the beginning of the experiment (here the pump operation)
    start: unix number giving the starting time of the experiment
    tz: time zone object
    returns the corresponding date (format dd/ mm/ yyyy  h: m: s)
    """
    now = sec + start  # gives a Unix time
    return datetime.date.fromtimestamp(now).strftime(fmt)

#print(secondToHumanTime(38400000, 1578930000))



from tkinter import *
import Pmw

def changeCoul(col):
    fen.configure(background = col)

def changeLabel():
    lab.configure(text = combo.get())

couleurs = ('navy', 'royal blue', 'steelblue1', 'cadet blue',
              'lawn green', 'forest green', 'dark red',
              'grey80','grey60', 'grey40', 'grey20')

fen = Pmw.initialise()
bou = Button(fen, text ="Test", command =changeLabel)
bou.grid(row =1, column =0, padx =8, pady =6)
lab = Label(fen, text ='néant', bg ='ivory')
lab.grid(row =1, column =1, padx =8)

combo = Pmw.ComboBox(fen, labelpos = NW,
                       label_text = 'Choisissez la couleur :',
                       scrolledlist_items = couleurs,
                       listheight = 150,
                       selectioncommand = changeCoul)
combo.grid(row =2, columnspan =2, padx =10, pady =10)

fen.mainloop()
