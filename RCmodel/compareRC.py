
import numpy as np
import matplotlib.pylab as plt
from models import R1C1sim
from planning import getRandomStart, tsToHuman
from dataengines import PyFina, getMeta

circuit = {"name":"Nord", "Text":5, "Tint":4}
interval = 3600
dir = "/var/opt/emoncms/phpfina"

wsize = 1 + 8*24*3600//interval

Cw = 1162.5 #Wh/m3/K
# flow_rate en m3/h
flow_rate = 5
max_power = flow_rate * Cw * 15

message = "quel circuit ?"
cir = input(message)
circuit["name"] = cir

meta = getMeta(circuit["Text"],dir)
fullLength = meta["npoints"] * meta["interval"]
_tss = meta["start_time"]
_tse = meta["start_time"]+fullLength
length = _tse - _tss
npoints =  length // interval

Text = PyFina(circuit["Text"], dir, _tss, interval, npoints)

# valeur initiale de température pour la convolution :
T0 = 15

# dictionnaire des différentes valeurs (R,C) :
if cir == "Cellule":
    Rvalues = [2.59e-4]
    Cvalues = [1.31e9]

if cir == "Nord":
    Rvalues = [2.95e-4, 3.30e-4, 5.20e-4, 1.06e-3]
    Cvalues = [1.89e9, 1.53e9, 1.31e9, 2.05e9]

if cir == "Sud":
    Rvalues = [9.85e-4, 1.89e-4, 1.14e-3]
    Cvalues = [2.19e9, 2.61e8, 4.14e8]


message = "quel mode ? \n 1 --> chauffage constant ; 2 --> pas de chauffage \n"
mode = input(message)
if mode == "1":
    Qc = np.ones(wsize)*max_power
else:
    Qc = np.zeros(wsize)

Ok = True

while True:
    ts = getRandomStart(_tss,_tse, 10, 5)
    ts = getRandomStart(_tss,_tse, 3, 7)
    pos = (ts - _tss) // interval
    Text_ep = Text[pos:pos+wsize]
    RCdata = []
    for i in range(len(Rvalues)):
        R = Rvalues[i]
        C = Cvalues[i]
        convo = R1C1sim(interval, R, C, Qc, Text_ep, T0)
        RCdata.append(convo)

    title = "Circuit {} \n timestamp {} / {}".format(cir, ts, tsToHuman(ts))

    xr = np.arange(ts, ts+wsize*interval, interval)
    for i in range(len(Rvalues)):
        plt.plot(xr, RCdata[i], label="R : {} // C : {}".format(Rvalues[i], Cvalues[i]))
    plt.plot(xr, Text_ep, '--', label='température extérieure')

    plt.legend(loc='lower left', ncol=2)
    plt.title(title)
    plt.show()
