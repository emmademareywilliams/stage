#!/usr/bin/env python3
"""
joue des épisodes avec des valeurs de (R,C) qui varient

"""

from RLtoolbox import Training, Environnement, initializeNN, visNN, saveNN


# le circuit
interval = 3600
# nombre d'intervalles sur lequel la simulation sera menée
wsize = 1 + 8*24*3600//interval
dir = "/var/opt/emoncms/phpfina"
import numpy as np
schedule = np.array([ [7,17], [7,17], [7,17], [7,17], [7,17], [-1,-1], [-1,-1] ])
Cw = 1162.5 #Wh/m3/K
max_power = 5 * Cw * 15

circuit = {"Text":5, "dir": dir,
           "schedule": schedule, "interval": interval, "wsize": wsize}

"""
Rfamily = [2e-4, 5e-4, 1e-3, 1e-1]
Cfamily = [2e8,  2e9,  2e9,  2e9]
# à changer selon la famille (R,C) qu'on veut utiliser :
i = 1
R = Rfamily[i]
C = Cfamily[i]
R= 3.08814171e-04
C= 8.63446560e+08
"""


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

class EnvIndus(Environnement):
    def play(self, datas):
        """
        simulation d'un pilotage industriel sur la base d'un agenda :
        - réduit nuit / weekend
        - préchauffage avant l'occupation
        - contrôle hystérésis pendant l'occupation
        """
        for i in range(1, datas.shape[0]):
            # par défaut, l'action correspond à l'occupation / la non occupation
            action = datas[i,3]/self._Tc
            if datas[i,3] == 0:
                # en période de non occupation, s'il fait trop froid dehors :
                if datas[i,1] < 10:
                    action = 0.4
                # on commence à chauffer 3h avant l'ouverture des locaux :
                if datas[i,4] <= 3:
                    action = 1
            else:
                # en occupation, hystérésis classique :
                if datas[i-1,2] > self._Tc + self._hh or datas[i-1,2] < self._Tc - self._hh :
                    action = datas[i-1,2] <= self._Tc
            datas[i,0] = action * self._max_power
            datas[i,2] = self.sim(datas, i)
        return datas

"""
si pas présent, à installer par python3 -m pip install click
cf https://palletsprojects.com/
"""
import click
#silent = click.prompt('silent mode ? ', type=bool)
#Tc = click.prompt('temperature de consigne ', type=int)
#N = click.prompt('nombre d\'épisodes à jouer ', type=int)
hh = 1
modes = ["occupation", "simple", "industriel"]
#mode = click.prompt('hysteresys simple ou en mode occupation ? ', type=click.Choice(modes))

@click.command()
@click.option('--agent_name', type=str)
@click.option('--silent', type=bool, prompt='silent mode = sans montrer les replays des épisodes ?')
@click.option('--tc', type=int, prompt='température de consigne en °C')
@click.option('--n', type=int, prompt='nombre d\'épisodes à jouer ')
@click.option('--mode', type=click.Choice(modes), prompt='hysteresys simple ou en mode occupation ?')

import argparse
parser = argparse.ArgumentParser(description='playing with R and C')
parser.add_argument("--R", action="store", help="valeur de R", default=3.08814171e-04, type=float)
parser.add_argument("--C", action="store", help="valeur de C", default=8.63446560e+08, type=float)
args = parser.parse_args()


def play(agent_name, silent, tc, n, mode):
    print(silent, tc, n, mode, agent_name)

    from tools import getTruth, pickName
    saved = False
    if agent_name:
        import os
        if os.path.isfile(agent_name):
            saved = True
    else:
        agent_name, saved = pickName()

    if saved == True:
        import tensorflow as tf
        agent = tf.keras.models.load_model(agent_name)

        visNN(agent)

        Text, agenda, _tss, _tse = getTruth(circuit, visualCheck = not silent)

        if mode == "simple":
            env = EnvHyst(Text, agenda, _tss, _tse, interval, wsize, max_power, tc, hh, R=args.R, C=args.C)
        elif mode == "occupation":
            env = EnvHystNocc(Text, agenda, _tss, _tse, interval, wsize, max_power, tc, hh, R=args.R, C=args.C)
        elif mode == "industriel":
            env = EnvIndus(Text, agenda, _tss, _tse, interval, wsize, max_power, tc, hh, R=args.R, C=args.C)

        sandbox = Training(agent_name, "play", env, agent, N=n)
        # timestamp pour lequel le modèle ne chauffe pas assez avec un débit de 5 et la famille 1 (R,C) :
        #sandbox.play(silent=False, ts=1610494340)
        #sandbox.play(silent=False, ts=1577269940)
        #sandbox.play(silent=False, ts=1589644200)
        #sandbox.play(silent=False, ts=1608928315)
        sandbox.run(silent=silent)
        RC = {"R": args.R, "C": args.C}
        sandbox.close(RC)

if __name__ == "__main__":
    play()
