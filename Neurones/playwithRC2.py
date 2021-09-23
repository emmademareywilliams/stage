"""
Fichier pour comparer le comportement de l'agent pour différentes valeurs de R et C
"""

from RLtoolbox import Training, visNN
from play import EnvHystNocc, EnvIndus, EnvHyst, Environnement
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


RC = [{"R": 3.08814171e-04, "C": 8.63446560e+08}, {"R": 5e-4, "C": 2e9}, {"R": 1e-3, "C": 2e9}]
#n = 500



class PlayRC:

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
            sandbox = Training(name, "play", env, agent, N=N)
            sandbox.run(silent=True)
            self._matstat[i, 2:] = sandbox.close(modelRC)[1:]

    def closeall(self):
        print("**** RESULTATS STATS **** \n")
        print("Pour Tc = {}, hh = {}, en mode {}, {} épisodes pour chaque (R,C) \n".format(Tc, hh, mode, N))
        for line in range(self._nbRun):
            for col in range(len(self._libelle)):
                label = self._libelle[col]
                print("{} : {} ".format(label, self._matstat[line][col]))
            if mode == 'industriel':
                pct = round(100*(self._matstat[line][9] - self._matstat[line][5])/self._matstat[line][9], 2)
                print("% gain agent : {}".format(pct))
            print("********* \n")


import click

silent = click.prompt('silent mode ? ', type=bool)
Tc = click.prompt('temperature de consigne ', type=int)
N = click.prompt('nombre d\'épisodes à jouer ', type=int)
hh = 1
modes = ["occupation", "simple", "industriel"]
mode = click.prompt('hysteresys simple ou en mode occupation ? ', type=click.Choice(modes))

"""
@click.command()
@click.option('--agent_name', type=str)
@click.option('--silent', type=bool, prompt='silent mode = sans montrer les replays des épisodes ?')
@click.option('--tc', type=int, prompt='température de consigne en °C')
@click.option('--n', type=int, prompt='nombre d\'épisodes à jouer ')
@click.option('--mode', type=click.Choice(modes), prompt='hysteresys simple ou en mode occupation ?')
"""

if __name__ == "__main__":

    from tools import getTruth, pickName

    playground = PlayRC(RC)
    #print(playground._nbRun)
    name, savedModel = pickName()

    if savedModel == True:
        import tensorflow as tf
        agent = tf.keras.models.load_model(name)

        visNN(agent)

        Text, agenda, _tss, _tse = getTruth(circuit, visualCheck=False)
        playground.multiplePlay(agent, name, Text, agenda, _tss, _tse)
        playground.closeall()
