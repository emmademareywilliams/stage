#!/usr/bin/env python3
"""
joue des épisodes

- demande à l'utilisateur de charger un réseau (fonction pickName)
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


class EnvHyst(Environnement):
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

class EnvHystNocc(Environnement):
    def play(self, datas):
        """
        fait jouer un contrôleur hysteresys à un modèle R1C1 en prenant en compte l'occupation
        """
        for i in range(1,datas.shape[0]):
            if datas[i-1,3] == 0 :
                # pas d'occupation - calcul à la cible
                Tint_sim = self.getR1C1toTarget(datas, i)
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

        return datas

if __name__ == "__main__":

    from tools import getTruth, pickName

    name, savedModel = pickName()

    if savedModel == True:
        import tensorflow as tf
        agent = tf.keras.models.load_model(name)
    else :
        agent = initializeNN(circuit["inputs_size"], circuit["numAct"], name)
        name = saveNN(agent, name, "raw")

    visNN(agent)

    Text, agenda, _tss, _tse = getTruth(circuit, visualCheck=True)

    env = EnvHystNocc(Text, agenda, _tss, _tse, interval, wsize)
    sandbox = Training(name, "play", env, agent)
    #sandbox.play(1589644200)
    #sandbox.play(1608928315)
    sandbox.run()
    sandbox.close()
