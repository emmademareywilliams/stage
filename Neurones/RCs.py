"""
code pour faire tourner le modèle sur différentes valeurs du couple (R, C)
puis affichage des différentes courbes à l'écran
    --> ici le réseau de neurones n'intervient pas !
    --> on veut simplement observer l'influence de R et C sur le comportement du contrôleur
"""

import numpy as np
import matplotlib.pylab as plt
from matplotlib.patches import Rectangle
from planning import tsToHuman, getRandomStart, getLevelDuration
import random
import signal
import time
import copy
import math
import sys
from models import R1C1variant, R1C1sim
from dataengines import PyFina, getMeta
from planning import tsToHuman, basicAgenda
from models import R1C1sim

exit = False

mode = 'R'
#mode = 'C'

circuit = {"name":"Nord", "Text":100, "Tint":4}
schedule = np.array([ [7,17], [7,17], [7,17], [7,17], [7,17], [-1,-1], [-1,-1] ])
interval = 3600
dir = "/var/opt/emoncms/phpfina"

wsize = 1 + 8*24*3600//interval

Cw = 1162.5 #Wh/m3/K
# flow_rate en m3/h
flow_rate = 5
max_power = flow_rate * Cw * 15

# température de consigne en °C
# confort temperature set point
Tc = 20

# demi-intervalle (en °C) pour le contrôle hysteresys
hh = 1


# dictionnaire des différentes valeurs (R,C) :
Rvalues = [3.08814171e-04, 3.08814171e-05, 3.08814171e-03]
Cvalues = [8.63446560e+08, 8.63446560e+07, 8.63446560e+09]
# pour le moment, on prendra les valeurs suivantes pour voi si la structure du code fonctionne :
# R = RCvalues[0][0]
# C = RCvalues[0][1]


class Environnement:
    """
    stocke les données décrivant l'environnement et offre des méthodes pour le caractériser
    """
    def __init__(self, Text, agenda, tss, tse, interval, wsize):
        self._Text = Text
        self._agenda = agenda
        self._tss = tss
        self._tse = tse
        self._interval = interval
        self._wsize = wsize

    def setStart(self, ts=None):
        """
        tire un timestamp aléatoirement avant fin mai OU après début octobre
        ou le fixe à une valeur donnée,si ts est fourni, pour rejouer un épisode (ex : 1588701000)

        retourne la position dans la timeserie et le timestamp correspondant
        """
        if ts is None:
            start = self._tss
            end = self._tse - self._wsize * self._interval - 4*24*3600
            #print(tsToHuman(start),tsToHuman(end))
            # on tire un timestamp avant fin mai OU après début octobre
            ts = getRandomStart(start, end, 10, 5)
        pos = (ts - self._tss) // self._interval
        tsvrai = self._tss + pos * self._interval

        print("*************************************")
        print("{} - {}".format(ts,tsToHuman(ts)))
        print("vrai={} - {}".format(tsvrai, tsToHuman(tsvrai)))
        return pos, tsvrai

    def buildEnv(self, pos):
        """
        retourne le tenseur des données de l'épisode
        - axe 0 = le temps
        - axe 1 = les paramètres
        nombre de paramètres pour décrire l'environnement
        3 paramètres physiques : Qc, Text et Tint
        dans la vraie vie, on pourrait rajouter le soleil mais le R1C1 n'en a pas besoin
        2 paramètres organisationnels :
        - temperature de consigne * occupation - si > 0 : bâtiment occupé,
        - nombre d'intervalles d'ici le changement d 'occupation, sorte de time of flight,
        """
        datas=np.zeros((self._wsize, 5))
        # condition initiale aléatoire
        datas[0,0] = random.randint(0,1)*max_power
        datas[0,2] = random.randint(17,20)
        # on connait Text (vérité terrain) sur toute la longueur de l'épisode
        datas[:,1] = self._Text[pos:pos+self._wsize]
        occupation = self._agenda[pos:pos+self._wsize+4*24*3600//self._interval]
        for i in range(self._wsize):
            datas[i,4] = getLevelDuration(occupation, i)
        # consigne
        datas[:,3] = Tc * occupation[0:self._wsize]
        print("condition initiale : Qc {:.2f} Text {:.2f} Tint {:.2f}".format(datas[0,0],datas[0,1],datas[0,2]))
        return datas

    def xr(self, tsvrai):
        """
        retourne le tableau des timestamps sur l'épisode
        """
        return np.arange(tsvrai, tsvrai+self._wsize*self._interval, self._interval)

    def getR1C1(self, datas, index, R, C):
        """
        calcule la température intérieure à l'index selon un modèle R1C1
        """
        _Qc = datas[index-1:index+1,0]
        _Text = datas[index-1:index+1,1]
        return R1C1variant(self._interval, R, C, _Qc, _Text, datas[index-1,2])

    def getR1C1variant(self, datas, index, pos, tof, R, C):
        """
        calcul de température par convolution
        utilisé dans le modèle avec occupation
        """
        Qc = np.ones(tof)*max_power
        # datas[i,1] correspond à Text[i+pos]
        Text = self._Text[pos+index-1:pos+index-1+tof]
        Tint = datas[index-1, 2]
        return R1C1sim(self._interval, R, C, Qc, Text, Tint)

    def play(self, datas, pos, R, C):
        """
        fait jouer un contrôleur hysteresys à un modèle R1C1 en prenant en compte l'occupation
        retourne le tenseur de données sources complété par le scénario de chauffage et la température intérieure simulée
        """
        for i in range(1,datas.shape[0]):
            if datas[i-1,3] == 0 :
                # pas d'occupation
                # on chauffe en fonction du tof
                tof = int(datas[i-1,4])
                # print("tof: {}, i: {}".format(tof, i))
                Tint_sim = self.getR1C1variant(datas, i, pos, tof, R, C)
                if Tint_sim[-1] < Tc - hh:
                    datas[i,0] = max_power

            else:
                # en occupation
                # hystérésis classique
                if datas[i-1,2] > Tc+hh or datas[i-1,2] < Tc-hh :
                    action = datas[i-1,2] <= Tc
                    datas[i,0] = action * max_power
                else:
                    # on est dans la fenêtre > on ne change rien :-)
                    datas[i,0] = datas[i-1,0]
            datas[i,2] = self.getR1C1(datas, i, R, C)

        # on vérifie si on a chauffé ou pas
        #heating =  np.sum(datas[index:,0]) > 0
        return datas



def playRC(env, mode, ts=None):

    pos, tsvrai = env.setStart(ts)
    xr = env.xr(tsvrai)
    adatas = env.buildEnv(pos)
    wsize = adatas.shape[0]
    RCdatas = []
    RCconso = []

    """
    mode R --> on fait varier la valeur de R
    """
    if mode == 'R':
        C = Cvalues[0]
        for i in range(len(Rvalues)):
            R = Rvalues[i]
            mdatas = env.play(copy.deepcopy(adatas), pos, R, C)
            mConso = int(np.sum(mdatas[1:,0]) / 1000)
            RCdatas.append(mdatas)
            RCconso.append(mConso)


        # matérialisation de la zone de confort par un hystéréris autour de la température de consigne
        zoneconfort = Rectangle((xr[0], Tc-hh), xr[-1]-xr[0], 2*hh, facecolor='g', alpha=0.5, edgecolor='None')

        title = "timestamp {} {}".format(tsvrai, tsToHuman(tsvrai))
        title = "Pour C constant : C = {}".format(C)

        ax1 = plt.subplot(211)
        plt.title(title)
        ax1.add_patch(zoneconfort)
        plt.ylabel("Temp. intérieure °C")
        plt.plot(xr, RCdatas[0][:,2], color='orange', label="R : {}".format(Rvalues[0]))
        plt.plot(xr, RCdatas[1][:,2], color="blue", label="R : {}".format(Rvalues[1]))
        plt.plot(xr, RCdatas[2][:,2], color="red", label="R : {}".format(Rvalues[2]))
        plt.legend(loc='lower right')


    """
    mode C --> on fait varier la valeur de C
    """
    if mode == 'C':
        R = Rvalues[0]
        for i in range(len(Cvalues)):
            C = Cvalues[i]
            mdatas = env.play(copy.deepcopy(adatas), pos, R, C)
            mConso = int(np.sum(mdatas[1:,0]) / 1000)
            RCdatas.append(mdatas)
            RCconso.append(mConso)


        # matérialisation de la zone de confort par un hystéréris autour de la température de consigne
        zoneconfort = Rectangle((xr[0], Tc-hh), xr[-1]-xr[0], 2*hh, facecolor='g', alpha=0.5, edgecolor='None')

        title = "timestamp {} {}".format(tsvrai, tsToHuman(tsvrai))
        title = "Pour R constant : R = {}".format(C)

        ax1 = plt.subplot(211)
        plt.title(title)
        ax1.add_patch(zoneconfort)
        plt.ylabel("Temp. intérieure °C")
        plt.plot(xr, RCdatas[0][:,2], color='orange', label="C : {}".format(Cvalues[0]))
        plt.plot(xr, RCdatas[1][:,2], color="blue", label="C : {}".format(Cvalues[1]))
        plt.plot(xr, RCdatas[2][:,2], color="red", label="C : {}".format(Cvalues[2]))
        plt.legend(loc='lower right')


    ax3 = plt.subplot(212, sharex=ax1)
    plt.ylabel("°C")
    plt.plot(xr, mdatas[:,3], label="consigne")
    plt.legend(loc='upper left')
    ax4 = ax3.twinx()
    plt.ylabel("nb intervalles > cgt occ.")
    plt.plot(xr, RCdatas[0][:,4],'o', markersize=1, color="red")

    plt.show()


def _sigint_handler(signal, frame):
    """
    Réception du signal de fermeture
    """
    print("signal de fermeture reçu")
    exit = True


def run(env):
    """
    boucle d'exécution
    """
    # Set signal handler to catch SIGINT or SIGTERM and shutdown gracefully
    signal.signal(signal.SIGINT, _sigint_handler)
    signal.signal(signal.SIGTERM, _sigint_handler)

    # Until asked to stop
    playRC(env, mode)
    plt.close()

def close():
    """
    à la fermeture, si on vient de procéder à un entrainement :
    - on enregistre le réseau
    - on produit les graphiques qualité
    """
    print("leaving the game")



if __name__ == "__main__":

    meta = getMeta(circuit["Tint"],dir)

    # durée du flux en secondes
    fullLength = meta["npoints"] * meta["interval"]
    print("Caractéristiques du flux de température extérieure")
    print("Démarrage : {}".format(meta["start_time"]))
    print("Fin: {}".format(meta["start_time"]+fullLength))
    print("Durée totale en secondes: {}".format(fullLength))

    _tss = meta["start_time"]
    _tse = meta["start_time"]+fullLength

    if _tse <= _tss :
        sys.exit()

    if _tse - _tss <= wsize*interval + 4*24*3600 :
        print("Vous n'aurez pas assez de données pour travailler : impossible de poursuivre")
        sys.exit()

    length = _tse - _tss
    npoints =  length // interval
    print(tsToHuman(_tss),tsToHuman(_tse))
    print("Vous allez travailler sur une durée de {} secondes".format(length))
    print("au pas de {} secondes, le nombre de points sera de {}".format(interval,npoints))
    print("pour information, la durée d'un épisode est de {} intervalles".format(wsize))
    input("pressez une touche pour continuer")

    Text = PyFina(circuit["Text"], dir, _tss, interval, npoints)

    agenda = basicAgenda(npoints,interval, _tss,-1,-1,schedule=schedule)

    """
    # affichage de la vérité terrain pour s'assurer qu'il n'y a pas de valeurs aberrantes
    plt.figure(figsize=(20, 10))
    ax1=plt.subplot(211)
    plt.plot(meta["start_time"]+Text.timescale(),Text, label='Text')
    plt.legend()
    ax2 = plt.subplot(212,  sharex=ax1)
    plt.plot(meta["start_time"]+Text.timescale(),agenda, label='occupation')
    plt.legend()
    plt.show()
    """

    env = Environnement(Text, agenda, _tss, _tse, interval, wsize)
    #sandbox = HystNOcc(name, mode, env, agent)
    #sandbox.play(1589644200)
    #sandbox.play(1608928315)
    run(env)
    close()
    plt.close()
