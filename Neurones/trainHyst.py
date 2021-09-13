#!/usr/bin/env python3
"""
entrainement en mode hysteresis
"""
from RLtoolbox import Training

# le circuit
interval = 3600
"""
nombre d'intervalles sur lequel la simulation sera menée
un entrainement sur 60 heures est possible lorsqu'on a 2 paramètres en entrée du réseau.
avec 4 paramètres en entrée, il faut soit augmenter le nombre d'épisodes, soit entrainer sur des épisodes de 8 jours
"""
#wsize = 1 + 60*3600//interval
wsize = 1 + 8*24*3600//interval
dir = "/var/opt/emoncms/phpfina"
import numpy as np
schedule = np.array([ [7,17], [7,17], [7,17], [7,17], [7,17], [-1,-1], [-1,-1] ])
Cw = 1162.5 #Wh/m3/K
max_power = 5 * Cw * 15
circuit = {"Text":1, "dir": dir,
           "schedule": schedule, "interval": interval, "wsize": wsize,
           "numAct": 2, "inputs_size": 4,
           "max_power": max_power, "Tc": 21, "hh": 1}

class Hysteresys(Training):
    def reward(self, datas, i):
        reward = - abs(datas[i,2] - self._env._Tc)
        return reward

if __name__ == "__main__":

    from tools import trainFromRaw

    trainFromRaw(circuit, Hysteresys, visualCheck=True)
