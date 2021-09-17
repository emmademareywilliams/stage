"""
Work in progress

idée = fichier qui permet de lancer les tests play de manière automatique, en faisant varier :
    - R et C pour un même réseau
    - le nom du réseau

Premier mode : pour un réseau fixé --> on entre le dictionnaire des couples (R,C), le nombre d'épisodes qu'on veut jouer
    --> pour chaque couple (R,C), le code lance les n épisodes de jeu
    --> on obtient une matrice de type self._stats pour chaque (R,C)
    --> on garde les stats générales en mémoire dans une autre matrice
"""

from RLtoolbox import Training, visNN
from play import EnvHystNocc, EnvIndus, EnvHyst, Environnement
import numpy as np
from play import Tc, hh, mode


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
        - 10 colonnes : couple (R,C) + (température moyenne en occupation, conso moyenne, nombre de points en luxe et en inconfort) resp. pour l'agent et le modèle
        """
        self._nbRun = len(self._RCdict)
        self._matstat = np.zeros((self._nbRun, 10))
        for i in range(self._nbRun):
            self._matstat[i][0] = self._RCdict[i]["R"]
            self._matstat[i][1] = self._RCdict[i]["C"]
        self._libelle = ["R", "C", "Tocc moy agent", "luxe agent", "inc agent", "conso agent", "Tocc moy modèle", "luxe modèle", "inc modèle", "conso modèle"]

    def multiplePlay(self, agent, name, Text, agenda, _tss, _tse):
        for i in range(self._nbRun):
            modelRC = self._RCdict[i]
            if mode == 'occupation':
                env = EnvHystNocc(Text, agenda, _tss, _tse, interval, wsize, max_power, Tc, hh, R=self._RCdict[i]["R"], C=self._RCdict[i]["C"])
            elif mode == 'simple':
                env = EnvHyst(Text, agenda, _tss, _tse, interval, wsize, max_power, Tc, hh, R=self._RCdict[i]["R"], C=self._RCdict[i]["C"])
            elif mode == 'industriel':
                env = EnvIndus(Text, agenda, _tss, _tse, interval, wsize, max_power, Tc, hh, R=self._RCdict[i]["R"], C=self._RCdict[i]["C"])
            sandbox = TrainingRC(name, "play", env, agent)
            sandbox.run(silent=True)
            self._matstat[i, 2:] = sandbox.close()[1:]

    def closeall(self):
        print("**** RESULTATS STATS **** \n")
        print("Pour Tc = {}, hh = {}, en mode {} \n".format(Tc, hh, mode))
        for line in range(self._nbRun):
            for col in range(len(self._libelle)):
                label = self._libelle[col]
                print("{} : {} ".format(label, self._matstat[line][col]))
            if mode == 'industriel':
                pct = round(100*(self._matstat[line][9] - self._matstat[line][5])/self._matstat[line][9], 2)
                print("% gain agent : {}".format(pct))
            print("********* \n")



if __name__ == "__main__":

    from tools import getTruth, pickName

    playground = PlayStat(RC)
    #print(playground._nbRun)
    name, savedModel = pickName()

    if savedModel == True:
        import tensorflow as tf
        agent = tf.keras.models.load_model(name)

        visNN(agent)

        Text, agenda, _tss, _tse = getTruth(circuit, visualCheck=False)
        playground.multiplePlay(agent, name, Text, agenda, _tss, _tse)
        playground.closeall()
