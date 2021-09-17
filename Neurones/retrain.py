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

import argparse
parser = argparse.ArgumentParser(description='retraining...')
parser.add_argument("--N", action="store", help="nombre d\'épisodes", default=900, type=int)
parser.add_argument("--k", action="store", help="paramètre k", default=0.6, type=float)
args = parser.parse_args()

class Retrain(Training):
    def reward(self, datas, i):
        if datas[i,3] != 0:
            reward = - abs( datas[i,2] - self._env._Tc)
        else:
            reward = - args.k * datas[i,0] / self._env._max_power
        return reward

if __name__ == "__main__":

    from tools import getTruth

    name = "hys20.h5"
    import os
    if os.path.isfile(name):
        import tensorflow as tf
        tf.config.set_visible_devices([], 'GPU')
        agent = tf.keras.models.load_model(name)

        Text, agenda, _tss, _tse = getTruth(circuit, visualCheck=False)
        env = Environnement(Text, agenda, _tss, _tse, circuit["interval"], circuit["wsize"], circuit["max_power"], circuit["Tc"], circuit["hh"])

        sandbox = Retrain(name, "train", env, agent, N=args.N)
        sandbox.run()
        sandbox.close(suffix="{}_retrained_k{}".format(name[:-3],str(args.k).replace(".","dot")))
    else:
        print("agent initial {} introuvable - impossible de continuer".format(name))
