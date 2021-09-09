
import numpy as np
import matplotlib.pylab as plt
from models import R1C1sim
from planning import tsToTuple, tsToHuman
from dataengines import PyFina, getMeta
import signal
import sys
import random

circuit = {"Text":1}
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
T0 = 15

"""
R représente l'isolation du bâtiment : plus la valeur de R est petite, moins il y d'isolation
C représente l'inertie du bâtiment : plus la valeur de C est grande, plus le bâtiment a de l'inertie

dictionnaire des différentes valeurs (R,C) :
Rvalues[0] --> circuit cellule
Rvalues[1:4] --> circuit Nord
Rvalues[5:7] --> circuit Sud
"""
Rvalues = [2.59e-4, 2.95e-4, 3.30e-4, 5.20e-4, 1.06e-3, 9.85e-4, 1.89e-4, 1.14e-3]
Cvalues = [1.31e9,  1.89e9,  1.53e9,  1.31e9,  2.05e9,  2.19e9,  2.61e8,  4.14e8]

"""
on distingue 4 grandes familles de couples (R,C)
la famille R=2e-4 C=2e8 est une passoire parfaite et la puissance de chauffage est sous-dimensionnée pour ce cas de figure
lors des épisodes très froids et même en chauffant en permamence, Tint peine à monter et est très sensible aux variations de Text
sans chauffage en hiver ou sans clim en été, on est à l'intérieur comme à l'extérieur
la famille R=1e-1 C=2e9 est une cave parfaite
ces 2 familles sont des caricatures pour forcer le trait et comprendre comment fonctionne l'analogie électrique
"""
Rfamily = [2e-4, 5e-4, 1e-3, 1e-1]
Cfamily = [2e8,  2e9,  2e9,  2e9]


season = input("quelle saison ? winter ? summer ?\n")

mode = "0"
energy = "pas de chauffage"
if season == "winter":
    message = "quel mode ? \n 1 --> chauffage constant ; 0 --> pas de chauffage \n"
    mode = input(message)

if mode == "1":
    Qc = np.ones(wsize)*max_power
    energy = "chauffage permanent"
else:
    Qc = np.zeros(wsize)*max_power

def _sigint_handler(signal, frame):
    print("fermeture")
    sys.exit(0)

signal.signal(signal.SIGINT, _sigint_handler)
signal.signal(signal.SIGTERM, _sigint_handler)

def getRandomStart(start, end, month_min, month_max, mode="winter"):
    """
    tire aléatoirement un timestamp dans un intervalle en faisant en sorte qu'il y ait assez de données pour la convolution
    s'assure que le mois du timestamp convient à la saison que l'on veut étudier (hiver, été)
    """
    while True:
        randomts = random.randrange(start, end - wsize * interval)
        month = tsToTuple(randomts).tm_mon
        if month in range(month_min, month_max) and mode=="summer":
            break
        if month not in range(month_min, month_max) and mode=="winter":
            break
    return randomts

while True:

    ts = getRandomStart(_tss,_tse, 5, 10, season)
    pos = (ts - _tss) // interval
    Text_ep = Text[pos:pos+wsize]

    title = "Timestamp {} / {}".format(ts, tsToHuman(ts))
    title = "{}\n {}".format(title, energy)
    plt.figure(figsize=(20, 10))
    plt.subplot(111)
    plt.title(title)
    plt.xlabel("Temps (heures)")
    plt.ylabel("Température (°C)")

    for i,R in enumerate(Rfamily):
        C = Cfamily[i]
        convo = R1C1sim(interval, R, C, Qc, Text_ep, T0)
        plt.plot(convo, '--', linewidth=2, label="R={:.2e} C={:.2e}".format(R,C))

    plt.plot(Text_ep, linewidth=3, label="température extérieure")
    plt.legend(loc='upper left', ncol=2)
    plt.show()
