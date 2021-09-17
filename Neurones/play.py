#!/usr/bin/env python3
"""
joue des épisodes

- demande à l'utilisateur de charger un réseau (fonction pickName)
- en initialise un aléatoirement si l'utilisateur ne donne pas d'indication ou un nom de fichier qui n'existe pas

"""

from RLtoolbox import Training, Environnement, initializeNN, visNN, saveNN

"""
à installer par python3 -m pip install click
cf https://palletsprojects.com/
"""
import click
silent = click.prompt('silent mode ? ', type=bool)
Tc = click.prompt('temperature de consigne ', type=int)
N = click.prompt('nombre d\'épisodes à jouer ', type=int)
hh = 1
modes = ["occupation", "simple"]
mode = click.prompt('hysteresys simple ou en mode occupation ? ', type=click.Choice(modes))

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
           "schedule": schedule, "interval": interval, "wsize": wsize}

Rfamily = [2e-4, 5e-4, 1e-3, 1e-1]
Cfamily = [2e8,  2e9,  2e9,  2e9]
# à changer selon la famille (R,C) qu'on veut utiliser :
i = 1
R = Rfamily[i]
C = Cfamily[i]
R= 3.08814171e-04
C= 8.63446560e+08


class EnvHyst(Environnement):
    def play(self, datas):
        """
        fait jouer un contrôleur hysteresys à un modèle R1C1
        """
        for i in range(1, datas.shape[0]):
            if datas[i-1,2] > self._Tc + self._hh or datas[i-1,2] < self._Tc - self._hh :
                action = datas[i-1,2] <= self._Tc
                datas[i,0] = action * self._max_power
            else:
                # on est dans la fenêtre > on ne change rien :-)
                datas[i,0] = datas[i-1,0]
            datas[i,2] = self.sim(datas, i)
        return datas

class EnvHystNocc(Environnement):
    def play(self, datas):
        """
        fait jouer un contrôleur hysteresys à un modèle R1C1 en prenant en compte l'occupation
        """
        for i in range(1,datas.shape[0]):
            if datas[i-1,3] == 0 :
                # pas d'occupation - calcul à la cible
                Tint_sim = self.sim2Target(datas, i)
                #print("i={} target {}".format(i, Tint_sim[-1]))
                if Tint_sim[-1] < self._Tc :
                    datas[i,0] = self._max_power

            else:
                # en occupation
                # hystérésis classique
                if datas[i-1,2] > self._Tc + self._hh or datas[i-1,2] < self._Tc - self._hh :
                    action = datas[i-1,2] <= self._Tc
                    datas[i,0] = action * self._max_power
                else:
                    # on est dans la fenêtre > on ne change rien :-)
                    datas[i,0] = datas[i-1,0]
            datas[i,2] = self.sim(datas, i)

        return datas

if __name__ == "__main__":

    from tools import getTruth, pickName

    name, savedModel = pickName()

    if savedModel == True:
        import tensorflow as tf
        agent = tf.keras.models.load_model(name)

        visNN(agent)

        Text, agenda, _tss, _tse = getTruth(circuit, visualCheck=True)

        if mode == "simple":
            env = EnvHyst(Text, agenda, _tss, _tse, interval, wsize, max_power, Tc, hh, R=R, C=C)
        elif mode == "occupation":
            env = EnvHystNocc(Text, agenda, _tss, _tse, interval, wsize, max_power, Tc, hh, R=R, C=C)

        sandbox = Training(name, "play", env, agent, N=N)
        # timestamp pour lequel le modèle ne chauffe pas assez avec un débit de 5 et la famille 1 (R,C) :
        #sandbox.play(silent=False, ts=1610494340)
        #sandbox.play(silent=False, ts=1577269940)
        #sandbox.play(silent=False, ts=1589644200)
        #sandbox.play(silent=False, ts=1608928315)
        sandbox.run(silent=silent)
        sandbox.close()
