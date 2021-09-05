#!/usr/bin/env python3
"""
entrainement en mode hysteresis
"""
from RLtoolbox import Training, Tc

# le circuit
interval = 3600
# nombre d'intervalles sur lequel la simulation sera menée
wsize = 1 + 60*3600//interval
dir = "/var/opt/emoncms/phpfina"
import numpy as np
schedule = np.array([ [7,17], [7,17], [7,17], [7,17], [7,17], [-1,-1], [-1,-1] ])
circuit = {"Text":1, "dir": dir, "schedule": schedule, "interval": interval, "wsize": wsize, "numAct": 2, "inputs_size": 4}

class Hysteresys(Training):
    def reward(self, datas, i):
        reward = - abs(datas[i,2] - Tc)
        return reward

if __name__ == "__main__":

    from tools import trainFromraw

    trainFromRaw(circuit, Hysteresys, visualCheck=True)
