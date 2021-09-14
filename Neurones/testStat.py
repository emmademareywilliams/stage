"""
idée = fichier qui permet de lancer les tests play de manière automatique, en faisant varier :
    - R et C pour un même réseau
    - le nom du réseau

Premier mode : pour un réseau fixé --> on entre le dictionnaire des couples (R,C), le nombre d'épisodes qu'on veut jouer
    --> pour chaque couple (R,C), le code lance les n épisodes de jeu
    --> on obtient une matrice de type self._stats pour chaque (R,C)
    --> on garde les stats générales en mémoire dans une autre matrice
"""

from RLtoolbox import Training, Environnement, initializeNN, visNN, saveNN
from play import EnvHystNocc
import numpy as np


# le circuit
interval = 3600
# nombre d'intervalles sur lequel la simulation sera menée
wsize = 1 + 8*24*3600//interval
dir = "/var/opt/emoncms/phpfina"
schedule = np.array([ [7,17], [7,17], [7,17], [7,17], [7,17], [-1,-1], [-1,-1] ])
Cw = 1162.5 #Wh/m3/K
max_power = 5 * Cw * 15

circuit = {"Text":5, "dir": dir,
           "schedule": schedule, "interval": interval, "wsize": wsize}

# pour l'instant, Tc et hh sont déclarés en global :
Tc = 20
hh = 1

RC = [{"R": 3.08814171e-04, "C": 8.63446560e+08}, {"R": 5e-4, "C": 2e9}, {"R": 1e-3, "C": 2e9}]
MAX_EPISODES = 500


class TrainingRC(Training):

    def close(self):
        print("leaving the game")
        stats = np.mean(self._stats, axis = 0)
        statsMoy = stats.round(1)
        print("statistiques pour les {} épisodes joués : \n".format(self._steps))
        print("Température intérieure moyenne en occupation : agent {} / modèle {} \n".format(statsMoy[1], statsMoy[5]))
        print("Consommation moyenne : agent {} / modèle {} \n".format(statsMoy[4], statsMoy[8]))
        print("Nombre de points en luxe : agent {} / modèle {} \n".format(statsMoy[2], statsMoy[6]))
        print("Nombre de points en inconfort : agent {} / modèle {} \n".format(statsMoy[3], statsMoy[7]))
        return statsMoy


class PlayStat:

    def __init__(self, RCdict):
        self._RCdict = RCdict
        """
        composantes de la matrice de stat :
        - nombre de lignes <--> nombre de couples (R,C) qu'on veut étudier
        - 8 colonnes : (température moyenne en occupation, conso moyenne, nombre de points en luxe et en inconfort) resp. pour l'agent et le modèle
        """
        self._nbRun = len(self._RCdict)
        self._matstat = np.zeros((self._nbRun, 8))

    def multiplePlay(self, agent, name, Text, agenda, _tss, _tse):
        for i in range(self._nbRun):
            modelRC = self._RCdict[i]
            env = EnvHystNocc(Text, agenda, _tss, _tse, interval, wsize, max_power, Tc, hh)
            sandbox = TrainingRC(name, "play", env, agent)
            sandbox.run(silent=True)
            mat = sandbox.close()
            self._matstat[i, :] = mat



if __name__ == "__main__":

    from tools import getTruth, pickName

    playground = PlayStat(RC)
    name, savedModel = pickName()

    if savedModel == True:
        import tensorflow as tf
        agent = tf.keras.models.load_model(name)

        visNN(agent)

        Text, agenda, _tss, _tse = getTruth(circuit, visualCheck=False)
        playground.multiplePlay(agent, name, Text, agenda, _tss, _tse)
