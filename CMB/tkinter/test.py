import datetime
import time
from dateutil import tz

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
combo.grid(row =2, column =2, padx =10, pady =10)

start = 1600900000
localstart = str(datetime.datetime.fromtimestamp(start))
date, clock = localstart.split(' ')
year, month, day = date.split('-')
hour, minute, second = clock.split(':')

#print(year, month, day)
#print(hour, minute, second)

monthDict = {}
for k in range(1,13):
    if k<=7:
        if k%2 == 1:
            monthDict[k] = 31
        else:
            monthDict[k] = 30
    if k>=8:
        if k%2 == 1:
            monthDict[k] = 30
        else:
            monthDict[k] = 31
monthDict[2] = 28
#print(monthDict)


limitday = monthDict[int(month)]
months = [int(month)]
days = [int(day)]
i = 0
for k in range(1,10):
    if int(day)+k == limitday +1:
        i=1
        days.append(i)
        months.append(int(month)+1)
    else:
        i = i+1
        if int(day)+k > limitday:
            days.append(i)
        else:
            days.append(int(day)+i)
#print(days, months)
hours = (k for k in range(1,25))


texte1 = Label(fen, text="Pump not in operation from:")
texte2 = Label(fen, text="to:")

dayCombo = Pmw.ComboBox(fen, labelpos = NW,
                       label_text = 'day',
                       scrolledlist_items = days,
                       listheight = 150)

monthCombo = Pmw.ComboBox(fen, labelpos = NW,
                       label_text = 'month',
                       scrolledlist_items = months,
                       listheight = 150)

hourCombo = Pmw.ComboBox(fen, labelpos = NW,
                       label_text = 'hour',
                       scrolledlist_items = hours,
                       listheight = 150)

# we must add selectioncommand = function in the arguments of the combo box so that a task is executed when
# we choose one of the values from the menu

texte1.grid(row =3, column =1)
dayCombo.grid(row =4, columnspan =1, padx=5)
monthCombo.grid(row =4, column =2, padx=0)
hourCombo.grid(row =4, column =3, padx=0)

#texte2.grid(row =4, column =1, padx =8)

fen.mainloop()
