# réentrainement

from RLtoolbox import Training, Environnement, visNN

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

k = 0.6

class Retrain(Training):
    def reward(self, datas, i):
        #prise en compte de la température ET de l'énergie via le facteur de pondération
        reward = 0
        if datas[i,3] != 0:
           reward = - abs( datas[i,2] - self._env._Tc)
        else:
           reward = - k * datas[i,0] / self._env._max_power
        return reward


if __name__ == "__main__":

    from tools import getTruth, pickName

    name, savedModel = pickName()

    if savedModel == True:
        import tensorflow as tf
        agent = tf.keras.models.load_model(name)

        visNN(agent)

        Text, agenda, _tss, _tse = getTruth(circuit, visualCheck=True)
        env = Environnement(Text, agenda, _tss, _tse, circuit["interval"], circuit["wsize"], circuit["max_power"], circuit["Tc"], circuit["hh"])

        sandbox = Retrain(name, "train", env, agent)
        sandbox.run()
        sandbox.close()
