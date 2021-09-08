
import numpy as np
import matplotlib.pylab as plt
from models import R1C1sim
from planning import getRandomStart, tsToHuman
from dataengines import PyFina, getMeta

circuit = {"Text":5, "Tint":4}
interval = 3600
dir = "/var/opt/emoncms/phpfina"

wsize = 1 + 8*24*3600//interval

Cw = 1162.5 #Wh/m3/K
# flow_rate en m3/h
flow_rate = 5
max_power = flow_rate * Cw * 15


meta = getMeta(circuit["Text"],dir)
fullLength = meta["npoints"] * meta["interval"]
_tss = meta["start_time"]
_tse = meta["start_time"]+fullLength
length = _tse - _tss
npoints =  length // interval

Text = PyFina(circuit["Text"], dir, _tss, interval, npoints)

# valeur initiale de température pour la convolution :
T0 = 20

# dictionnaire des différentes valeurs (R,C) :
# Rvalues[0] --> circuit cellule
# Rvalues[1:4] --> circuit Nord
# Rvalues[5:7] --> circuit Sud

Rvalues = [2.59e-4, 2.95e-4, 3.30e-4, 5.20e-4, 1.06e-3, 9.85e-4, 1.89e-4, 1.14e-3]
Cvalues = [1.31e9, 1.89e9, 1.53e9, 1.31e9, 2.05e9, 2.19e9, 2.61e8, 4.14e8]


message = "quel mode ? \n 1 --> chauffage constant ; 2 --> pas de chauffage \n"
mode = input(message)
if mode == "1":
    Qc = np.ones(wsize)
else:
    Qc = np.zeros(wsize)

while True:
    ts = getRandomStart(_tss,_tse, 10, 5)
    pos = (ts - _tss) // interval
    Text_ep = Text[pos:pos+wsize]
    RCdata = []
    for i in range(len(Rvalues)):
        R = Rvalues[i]
        C = Cvalues[i]
        convo = R1C1sim(interval, R, C, Qc, Text_ep, T0)
        RCdata.append(convo)

    title = "Timestamp {} / {}".format(ts, tsToHuman(ts))

    xr = np.arange(ts, ts+wsize*interval, interval)
    for i in range(len(Rvalues)):
        if i==0:
            plt.plot(RCdata[i], label="Cellule : R : {0:.2e} // C : {0:.2e}".format(Rvalues[i], Cvalues[i]))
        if i in range(1,4):
            plt.plot(RCdata[i], 'o', label="Nord : R : {0:.2e} // C : {0:.2e}".format(Rvalues[i], Cvalues[i]))
        if i in range(5,7):
            plt.plot(RCdata[i], '--', label="Sud : R : {0:.2e} // C : {0:.2e}".format(Rvalues[i], Cvalues[i]))
    plt.plot(Text_ep, '--', label="température extérieure")

    plt.legend(loc='lower left', ncol=2)
    plt.title(title)
    plt.xlabel("Temps (heures)")
    plt.ylabel("Température (°C)")
    plt.show()
