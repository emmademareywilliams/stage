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

class Train(Training):
    def reward(self, datas, i):
        if datas[i,3] != 0:
            reward = - abs( datas[i,2] - self._env._Tc)
        else:
            reward = - args.k * datas[i,0] / self._env._max_power
        return reward

class TrainWvote(Training):
    def reward(self, datas, i):
          l0 = self._env._Tc - 5 * self._env._hh
          l1 = self._env._Tc - 3 * self._env._hh
          l2 = self._env._Tc - self._env._hh
          l3 = self._env._Tc + self._env._hh
          if datas[i,3] != 0:
              reward = - abs( datas[i,2] - self._env._Tc)
              if datas[i-1,3] == 0:
                  if datas[i,2] < l0:
                      reward -= 30
                  if datas[i,2] < l1:
                      reward -= 30
                  if datas[i,2] < l2:
                      reward -= 20
                  # vu qu'on est en récompense négative, ces 2 lignes sont probablement surperflues
                  # et viennent peut-être brouiller la convergence
                  if l2 <= datas[i,2] <= l3 :
                      reward += 10
                  if self._env._Tc <= datas[i,2] <= l3 :
                      reward += 20
          else:
              reward = -  args.k * datas[i,0] / self._env._max_power
          return reward

class TrainWvote2(Training):
    def reward(self, datas, i):
          l0 = self._env._Tc - self._env._hh
          l1 = self._env._Tc + self._env._hh
          reward = 0
          if datas[i,3] != 0:
              if abs( datas[i,2] - self._env._Tc ) < self._env._hh:
                  reward += 1
              if datas[i-1,3] == 0:
                  if l0 <= datas[i,2] < self._env._Tc :
                      reward += 100
                  if self._env._Tc <= datas[i,2] <= l1 :
                      reward += 60
          else:
              if datas[i,0] == 0:
                  reward += args.k
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

        sandbox = TrainWvote2(name, "train", env, agent, N=args.N)
        sandbox.run()
        sandbox.close(suffix="{}_retrained_k{}".format(name[:-3],str(args.k).replace(".","dot")))
    else:
        print("agent initial {} introuvable - impossible de continuer".format(name))
