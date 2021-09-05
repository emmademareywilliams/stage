"""
outils et méthodes autour des classes de RLtoolbox

version beta : work in progress
"""

from RLtoolbox import Training, Environnement, initializeNN, visNN, saveNN, Tc, hh, max_power
from PyFina import PyFina, getMeta
import matplotlib.pylab as plt
from planning import tsToHuman, basicAgenda

def getTruth(circuit, visualCheck):
    """
    circuit : dictionnaire des paramètres du circuit

    exemple :
    ```
    import numpy as np
    schedule = np.array([ [7,17], [7,17], [7,17], [7,17], [7,17], [-1,-1], [-1,-1] ])
    circuit = {"Text":1, "dir": "/var/opt/emoncms/phpfina",
               "schedule": schedule, "interval": 3600, "wsize": 1 + 8*24,
               "numAct": 2, "inputs_size": 4}
    ```
    récupère la vérité terrain :
    - température extérieure
    - agenda d'occupation
    - timestamps de début(_tss) et de fin(_tse)
    """

    feedid = circuit["Text"]
    dir = circuit["dir"]
    schedule = circuit["schedule"]
    interval = circuit["interval"]
    wsize = circuit["wsize"]

    meta = getMeta(feedid, dir)
    # durée du flux en secondes
    fullLength = meta["npoints"] * meta["interval"]
    _tss = meta["start_time"]
    _tse = meta["start_time"]+fullLength
    npoints =  fullLength // interval

    _tss = meta["start_time"]
    _tse = meta["start_time"]+fullLength

    if _tse - _tss <= wsize*interval + 4*24*3600 :
        print("Vous n'aurez pas assez de données pour travailler : impossible de poursuivre")
        sys.exit()

    print("| ____|_ ____   _(_)_ __ ___  _ __  _ __ ___   ___ _ __ | |_")
    print("|  _| | '_ \ \ / / | '__/ _ \| '_ \| '_ ` _ \ / _ \ '_ \| __|")
    print("| |___| | | \ V /| | | | (_) | | | | | | | | |  __/ | | | |_")
    print("|_____|_| |_|\_/ |_|_|  \___/|_| |_|_| |_| |_|\___|_| |_|\__|")

    print("Démarrage : {}".format(meta["start_time"]))
    print("Durée totale en secondes: {}".format(fullLength))
    print("Fin: {}".format(meta["start_time"]+fullLength))
    print("De {} à {}".format(tsToHuman(_tss),tsToHuman(_tse)))
    print("au pas de {} secondes, le nombre de points sera de {}".format(interval,npoints))
    print("pour information, la durée d'un épisode est de {} intervalles".format(wsize))

    Text = PyFina(feedid, dir, _tss, interval, npoints)

    agenda = basicAgenda(npoints,interval, _tss,-1,-1,schedule=schedule)

    if visualCheck:
        ax1 = plt.subplot(211)
        plt.title("vérité terrain")
        plt.plot(Text, label="Text")
        plt.legend()
        plt.subplot(212, sharex=ax1)
        plt.plot(agenda, label="agenda")
        plt.legend()
        plt.show()

    return Text, agenda, _tss, _tse

def train(circuit, training, visualCheck=False):
    """
    circuit : dictionnaire des paramètres du circuit

    training : instance de la classe Training avec sa fonction reward définie
    """
    import tensorflow as tf

    interval = circuit["interval"]
    wsize = circuit["wsize"]
    numAct = circuit["numAct"]
    inputs_size = circuit["inputs_size"]

    # pour utiliser le CPU et non le GPU
    tf.config.set_visible_devices([], 'GPU')

    Text, agenda, _tss, _tse = getTruth(circuit, visualCheck)

    env = Environnement(Text, agenda, _tss, _tse, interval, wsize)

    name = "RL.h5"
    agent = initializeNN(inputs_size, numAct, name)
    name = saveNN(agent, name,"raw")
    visNN(agent)
    sandbox = training(name, "train", env, agent)
    sandbox.run()
    sandbox.close()
