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
circuit = {"name":"Nord", "Text":5, "Tint":4}

schedule = np.array([ [7,17], [7,17], [7,17], [7,17], [7,17], [-1,-1], [-1,-1] ])

dir = "/var/opt/emoncms/phpfina"

# sampling interval in seconds
interval = 3600
#interval = 900

# nombre d'intervalles sur lequel la simulation sera menée
# 60 correspond à un weekend
wsize = 1 + 60*3600//interval
#wsize = 1 + 8*24*3600//interval

# nombre d'actions possibles  : 2 = on chauffe ou pas
numAct = 2

# nombre de paramètres à fournir au réseau pour prédire l'action à exécuter à l'étape i
# cas 1 : on se limite à lui donner Text[i-1], Tint[i-1]
inputs_size = 2
# cas 2 : on fournit au réseau Text[i-1], Tint[i-1], Tc*occupation[i-1], tof[i-1]
# Tc est la température de consigne
# tof représente le nombre d'intervalles d'içi le changement d'occupation
#inputs_size = 4

class Env(Environnement):
    def play(self, datas):
        """
        fait jouer un contrôleur hysteresys à un modèle R1C1
        """
        for i in range(1, datas.shape[0]):
            if datas[i-1,2] > Tc+hh or datas[i-1,2] < Tc-hh :
                action = datas[i-1,2] <= Tc
                datas[i,0] = action * max_power
            else:
                # on est dans la fenêtre > on ne change rien :-)
                datas[i,0] = datas[i-1,0]
            datas[i,2] = self.getR1C1(datas, i)
        return datas

class Hysteresys(Training):
    def reward(self, datas, i):
        """
        la récompense correspondant à un comportement hysteresys
        """
        reward = - abs(datas[i,2] - Tc)
        return reward

if __name__ == "__main__":

    mode = input("train/play ?")

    readline.set_completer_delims('\t')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(simplePathCompleter)
    name = input("nom du réseau ?")
    if not name:
        name = "RL.h5"

    if ".h5" not in name:
        name = "{}.h5".format(name)

    savedModel = False
    if os.path.isfile(name):
        savedModel = True

    import tensorflow as tf

    if savedModel == True:
        agent = tf.keras.models.load_model(name)
    else :
        agent = initializeNN(inputs_size, numAct, name)
        name = saveNN(agent, name," raw")

    visNN(agent)

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

    # affichage de la vérité terrain pour s'assurer qu'il n'y a pas de valeurs aberrantes
    plt.figure(figsize=(20, 10))
    ax1=plt.subplot(211)
    plt.plot(meta["start_time"]+Text.timescale(),Text, label='Text')
    plt.legend()
    ax2 = plt.subplot(212,  sharex=ax1)
    plt.plot(meta["start_time"]+Text.timescale(),agenda, label='occupation')
    plt.legend()
    plt.show()

    env = Env(Text, agenda, _tss, _tse, interval, wsize)
    sandbox = Hysteresys(name, mode, env, agent)
    sandbox.run()
    sandbox.close()
    plt.close()
