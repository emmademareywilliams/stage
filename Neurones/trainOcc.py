#!/usr/bin/env python3
"""
entrainement en mode occupation
"""
from RLtoolbox import Training, Tc

# le circuit
interval = 3600
# nombre d'intervalles sur lequel la simulation sera menée
wsize = 1 + 8*24*3600//interval
dir = "/var/opt/emoncms/phpfina"
import numpy as np
schedule = np.array([ [7,17], [7,17], [7,17], [7,17], [7,17], [-1,-1], [-1,-1] ])
circuit = {"Text":5, "dir": dir, "schedule": schedule, "interval": interval, "wsize": wsize, "numAct": 2, "inputs_size": 4}

#facteur de pondération entre température et énergie (utilisé dans rewardBis) :
k = 0.6
# pour utiliser une récompense positive :
k = 1

class HystNOcc(Training):
    """
    def reward(self, datas, i):
        reward = - abs( datas[i,2] - Tc )
        if datas[i,3] == 0:
            if datas[i,0] != 0:
                reward -= datas[i,4] / 10
        return reward

    # ci-dessous des fonctions de récompense alternatives :

    def reward(self, datas, i):
        #prise en compte de la température ET de l'énergie via le facteur de pondération
        reward = 0
        if datas[i,3] != 0:
           reward = - abs( datas[i,2] - Tc )
        else:
           reward -= k*datas[i,0]/max_power
        return reward

    """
    def reward(self, datas, i):
        #essai avec une récompense positive
        reward = 0
        if datas[i,3] != 0:
            if abs( datas[i,2] - Tc ) < 1:
                reward = 1

        if datas[i,0]==0:
            reward = k
        return reward

if __name__ == "__main__":

    from tools import trainFromRaw

    trainFromRaw(circuit, HystNOcc)
