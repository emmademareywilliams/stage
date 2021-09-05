#!/usr/bin/env python3
"""
joue des épisodes

- demande à l'utilisateur de charger un réseau
- en initialise un aléatoirement si l'utilisateur ne donne pas d'indication ou un nom de fichier qui n'existe pas

"""

from RLtoolbox import Training, Environnement, initializeNN, visNN, saveNN, Tc, hh, max_power

# le circuit
interval = 3600
# nombre d'intervalles sur lequel la simulation sera menée
wsize = 1 + 8*24*3600//interval
dir = "/var/opt/emoncms/phpfina"
import numpy as np
schedule = np.array([ [7,17], [7,17], [7,17], [7,17], [7,17], [-1,-1], [-1,-1] ])
circuit = {"Text":1, "dir": dir, "schedule": schedule, "interval": interval, "wsize": wsize, "numAct": 2, "inputs_size": 4}


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

if __name__ == "__main__":

    # pour l'autocompletion en ligne de commande
    import readline
    import os
    import glob

    def simplePathCompleter(text,state):
        """
        tab completer pour les noms de fichiers, chemins....
        """
        line   = readline.get_line_buffer().split()

        return [x for x in glob.glob(text+'*')][state]

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
        name = saveNN(agent, name,"raw")

    visNN(agent)

    from tools import getTruth

    Text, agenda, _tss, _tse = getTruth(circuit, visualCheck=True)

    env = Env(Text, agenda, _tss, _tse, interval, wsize)
    sandbox = Training(name, "play", env, agent)
    #sandbox.play(1589644200)
    #sandbox.play(1608928315)
    sandbox.run()
    sandbox.close()
