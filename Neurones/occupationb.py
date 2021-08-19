#!/usr/bin/env python3
"""
training an agent recreating the behavior of a hysteresis controller
"""

from RLtoolbox import Training, Environnement, initializeNN, visNN, saveNN, simplePathCompleter, Tc, hh, max_power
import readline
import os
from dataengines import PyFina, getMeta
import matplotlib.pylab as plt
import numpy as np
from planning import tsToHuman, basicAgenda
from models import R1C1sim

# le circuit
# numéro de flux sur le serveur local synchronisé avec le serveur de terrain via le module sync
circuit = {"name":"Nord", "Text":100, "Tint":4}

schedule = np.array([ [7,17], [7,17], [7,17], [7,17], [7,17], [-1,-1], [-1,-1] ])

dir = "/var/opt/emoncms/phpfina"

# sampling interval in seconds
interval = 3600
#interval = 900

# nombre d'intervalles sur lequel la simulation sera menée
# 60 correspond à un weekend
#wsize = 1 + 60*3600//interval
# pour visualiser l'influence de l'occupation :
wsize = 1 + 8*24*3600//interval

# nombre d'actions possibles  : 2 = on chauffe ou pas
numAct = 2

# nombre de paramètres à fournir au réseau pour prédire l'action à exécuter à l'étape i
# cas 1 : on se limite à lui donner Text[i-1], Tint[i-1]
inputs_size = 2
# cas 2 : on fournit au réseau Text[i-1], Tint[i-1], Tc*occupation[i-1], tof[i-1]
# Tc est la température de consigne
# tof représente le nombre d'intervalles d'içi le changement d'occupation
inputs_size = 4


class Env(Environnement):
    def play(self, datas, pos):
        """
        fait jouer un contrôleur hysteresys à un modèle R1C1 en prenant en compte l'occupation
        """
        for i in range(1,datas.shape[0]):
            if datas[i-1,3] == 0 :
                # pas d'occupation
                # on chauffe en fonction du tof
                tof = int(datas[i-1,4])
                # print("tof: {}, i: {}".format(tof, i))
                Tint_sim = self.getR1C1variant(datas, i, pos, tof)
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
            datas[i,2] = self.getR1C1(datas, i)

        # on vérifie si on a chauffé ou pas
        #heating =  np.sum(datas[index:,0]) > 0
        return datas

class HystNOcc(Training):
    def reward(self, datas, i):
        """
        la récompense correspondant à un comportement hysteresys avec occupation
        reprend le mode C du code initial
        """
        if datas[i,3] == 0 and datas[i,2] <= Tc+hh:
            # le bâtiment n'est pas occupé ET la température est hors de la zone de confort
            reward = - abs(datas[i,2]-Tc)/(datas[i,4]+1)
        else:
            # on retrouve l'hystérésis classique
            reward = - abs(datas[i,2] - Tc)
        return reward


if __name__ == "__main__":

    import tensorflow as tf

    meta = getMeta(circuit["Tint"],dir)

    # durée du flux en secondes
    fullLength = meta["npoints"] * meta["interval"]
    print("Caractéristiques du flux de température extérieure")
    print("Démarrage : {}".format(meta["start_time"]))
    print("Fin: {}".format(meta["start_time"]+fullLength))
    print("Durée totale en secondes: {}".format(fullLength))

    _tss = meta["start_time"]
    _tse = meta["start_time"]+fullLength

    length = _tse - _tss
    npoints =  length // interval
    print(tsToHuman(_tss),tsToHuman(_tse))
    print("Vous allez travailler sur une durée de {} secondes".format(length))
    print("au pas de {} secondes, le nombre de points sera de {}".format(interval,npoints))
    print("pour information, la durée d'un épisode est de {} intervalles".format(wsize))

    Text = PyFina(circuit["Text"], dir, _tss, interval, npoints)

    agenda = basicAgenda(npoints,interval, _tss,-1,-1,schedule=schedule)

    env = Env(Text, agenda, _tss, _tse, interval, wsize)

    for i in range(6):
        name = "RL.h5"
        agent = initializeNN(inputs_size, numAct, name)
        name = saveNN(agent, name," raw")
        visNN(agent)
        sandbox = HystNOcc(name, "train", env, agent)
        sandbox.run()
        sandbox.close()
        plt.close()
