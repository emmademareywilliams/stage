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

# le circuit
# numéro de flux sur le serveur local synchronisé avec le serveur de terrain via le module sync
circuit = {"Text":5, "Tint":4}

schedule = np.array([ [7,17], [7,17], [7,17], [7,17], [7,17], [-1,-1], [-1,-1] ])

dir = "/var/opt/emoncms/phpfina"

# sampling interval in seconds
interval = 3600

# nombre d'intervalles sur lequel la simulation sera menée
wsize = 1 + 8*24*3600//interval

# nombre d'actions possibles  : 2 = on chauffe ou pas
numAct = 2

# nombre de paramètres à fournir au réseau pour prédire l'action à exécuter à l'étape i
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
        if datas[i,3] == 0:
            reward =  - datas[i,0] / max_power
        else :
            # occupation : hysteresys
            reward = - abs( datas[i,2] - Tc )
        if datas[i,3] != 0 and datas[i-1,3] == 0:
            if datas[i,2] <= Tc - hh :
                reward -= 100
        return reward


if __name__ == "__main__":

    import tensorflow as tf

    # pour utiliser le CPU et non le GPU
    tf.config.set_visible_devices([], 'GPU')

    meta = getMeta(circuit["Tint"],dir)
    # durée du flux en secondes
    fullLength = meta["npoints"] * meta["interval"]
    _tss = meta["start_time"]
    _tse = meta["start_time"]+fullLength
    npoints =  fullLength // interval

    print("Démarrage : {}".format(meta["start_time"]))
    print("Durée totale en secondes: {}".format(fullLength))
    print("Fin: {}".format(meta["start_time"]+fullLength))
    print(tsToHuman(_tss),tsToHuman(_tse))
    print("au pas de {} secondes, le nombre de points sera de {}".format(interval,npoints))
    print("pour information, la durée d'un épisode est de {} intervalles".format(wsize))

    Text = PyFina(circuit["Text"], dir, _tss, interval, npoints)

    agenda = basicAgenda(npoints,interval, _tss,-1,-1,schedule=schedule)

    env = Env(Text, agenda, _tss, _tse, interval, wsize)

    name = "RL.h5"
    agent = initializeNN(inputs_size, numAct, name)
    name = saveNN(agent, name," raw")
    visNN(agent)
    sandbox = HystNOcc(name, "train", env, agent)
    sandbox.run()
    sandbox.close()
    plt.close()
