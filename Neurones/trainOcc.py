#!/usr/bin/env python3
"""
entrainement en mode occupation
"""
from RLtoolbox import Training

# le circuit
interval = 3600
# nombre d'intervalles sur lequel la simulation sera menée
wsize = 1 + 8*24*3600//interval
dir = "/var/opt/emoncms/phpfina"
import numpy as np
schedule = np.array([ [7,17], [7,17], [7,17], [7,17], [7,17], [-1,-1], [-1,-1] ])
Cw = 1162.5 #Wh/m3/K
max_power = 5 * Cw * 15
circuit = {"Text":1, "dir": dir,
           "schedule": schedule, "interval": interval, "wsize": wsize,
           "numAct": 2, "inputs_size": 4,
           "max_power": max_power, "Tc": 20, "hh": 1}

class HystNOcc(Training):
    def reward(self, datas, i):
        reward = - abs( datas[i,2] - self._env._Tc )
        if datas[i,3] == 0:
            if datas[i,0] != 0:
                reward -= datas[i,4] / 10
        return reward

if __name__ == "__main__":

    from tools import trainFromRaw

    trainFromRaw(circuit, HystNOcc)
