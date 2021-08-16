#!/usr/bin/env python3
"""
reinforcement learning
training an agent recreating the behavior of a hysteresis controller
"""
import numpy as np
# nombre d'épisodes que l'on souhaite jouer
# pour jouer à l'infini, mettre MAX_EPISODES = None
# dans le cas d'un entrainement à l'infini, attention dans ce cas à la mémoire vive
# à surveiller via la commande free
MAX_EPISODES = 900

# taille d'un batch d'entrainement
BATCH_SIZE = 50
# taille de la mémoire du réseau
MEMORY_SIZE = 50000

MAX_EPS = 1
MIN_EPS = 0.01
# decay parameter
# c'est lui qui détermine la part d'aléatoire dans l'entrainement
# c'est-à-dire qui met le curseur entre exploration (aléatoire) et exploitation (utilisation du réseau)
# au fur et à mesure que l'on a exploré ce que donnaient des solutions aléatoires, il faut exploiter
# pour que le réseau puisse converger vers la politique optimale correspondant au problème posé
# on l'appelle aussi eligibility trace decay quant on fait du TD(lambda) ce qui n'est pas le cas içi
# TD = temporal difference
# içi on fait du TD simple, celui mis au point par Chris Watkins
LAMBDA = 0.001
LAMBDA = 0.0005
# discount parameter
# plus cette valeur est petite, moins on tient compte des récompenses différées
# = on donne plus d'importance aux récompenses immédiates
GAMMA = 0.099
#GAMMA = 0.05

dir = "/var/opt/emoncms/phpfina"

# sampling interval in seconds
interval = 3600
#interval = 900
schedule = np.array([ [7,17], [7,17], [7,17], [7,17], [7,17], [-1,-1], [-1,-1] ])

# le circuit
# flow_rate en m3/h
# numéro de flux sur le serveur local synchronisé avec le serveur de terrain via le module sync
circuit = {"name":"Nord", "Text":9, "Tint":4, "flow_rate":5}
# changer Text: 1 en Text: 9 pour travailler avec les données du collège Marc Bloch

Cw = 1162.5 #Wh/m3/K
max_power = circuit["flow_rate"] * Cw * 15

# température de consigne en °C
# confort temperature set point
Tc = 20

# le modèle qui va décrire l'évolution de la température intérieure
# un modèle électrique équivalent de type R1C1
R = 3.08814171e-04
C = 8.63446560e+08

# demi-intervalle (en °C) pour le contrôle hysteresys
hh = 1

# nombre d'actions possibles  : 2 = on chauffe ou pas
# pour l'instant, on reste simple
numAct = 2

# nombre d'intervalles sur lequel la simulation sera menée
# 60 correspond à un weekend
wsize = 1 + 60*3600//interval
#wsize = 1 + 8*24*3600//interval

# nombre de paramètres à fournir au réseau pour prédire l'état suivant à partir de l'état actuel
# cas 1 : on se limite à lui donner Tint[-1], Text[0]
inputs_size = 2
# cas 2 : on fournit au réseau Tint[-1], Text[0], Tc*occupation[0], tof[0]
# tof représente le nombre d'intervalles d'içi le changement d'occupation
# Tc est la température de consigne
#inputs_size = 4

import os
import sys
import matplotlib.pylab as plt
from matplotlib.patches import Rectangle
from planning import tsToTuple, tsToHuman, getRandomStart, basicAgenda, getLevelDuration, hmTots
import random
import signal
import time

import copy

import math

from models import R1C1sim, R1C1variant
from dataengines import PyFina, getMeta

# pour l'autocompletion en ligne de commande
import readline
import glob

def simplePathCompleter(text,state):
    """
    tab completer pour les noms de fichiers, chemins....
    """
    line   = readline.get_line_buffer().split()

    return [x for x in glob.glob(text+'*')][state]


def initializeNN(inputs_size, name):
    """
    initialisation du réseau neurone qui jouera le rôle de contrôleur ou agent énergétique
    son rôle est de produire l'action énergétique (chauffage On ou Off)
    La détermination de Tint après application de cette action est faite :
    - soit par le modèle par calcul
    - soit par l'environnement réel par monitoring
    """
    tf.keras.backend.set_floatx('float64')
    inputs = tf.keras.Input(shape=(inputs_size, ), name='states')
    x = tf.keras.layers.Dense((50), activation='relu')(inputs)
    # pour ajouter de la profondeur (pas utilisé pour l'instant)
    #x = tf.keras.layers.Dense((50), activation='relu')(x)
    outputs = tf.keras.layers.Dense(numAct,activation='linear', name='output')(x)
    agent = tf.keras.Model(inputs=inputs,outputs=outputs,name=name)
    agent.compile(loss="mse",optimizer="adam",metrics=['mae'])
    print("initialisation de l'agent terminée")
    print("inputs size : {}".format(inputs_size))
    return agent

def visNN(agent):
    """
    visualisation des poids du réseau
    """
    agent.summary()
    #print(agent.get_weights())

def setStart(ts=None, wsize = wsize):
    """
    tire un timestamp aléatoirement avant fin mai OU après début octobre
    ou le fixe à une valeur donnée pour rejouer un épisode (ex : 1588701000)
    retourne la position dans la timeserie et le timestamp correspondant
    """
    if ts is None:
        start = _tss
        end = _tse - wsize * interval - 4*24*3600
        #print(tsToHuman(start),tsToHuman(end))
        # on tire un timestamp avant fin mai OU après début octobre
        ts = getRandomStart(start, end, 10, 5)
    pos = (ts - _tss) // interval
    tsvrai = _tss + pos * interval

    print("*************************************")
    print("{} - {}".format(ts,tsToHuman(ts)))
    print("vrai={} - {}".format(tsvrai, tsToHuman(tsvrai)))
    return pos, tsvrai

def buildEnv(pos, wsize = wsize):
    """
    retourne le tenseur des données datas
    - axe 0 = le temps
    - axe 1 = les paramètres
    nombre de paramètres pour décrire l'environnement
    3 paramètres physiques : Qc, Text et Tint
    dans la vrai vie, on pourrait rajouter le soleil mais le R1C1 n'en a pas besoin
    3 paramètres organisationnels :
    - occupation O/N,
    - nombre d'intervalles d'ici le changement d 'occupation, sorte de time of flight,
    - temperature de consigne * occupation
    """
    datas=np.zeros((wsize, 6))
    # condition initiale aléatoire
    datas[0,0] = random.randint(0,1)*max_power
    datas[0,2] = random.randint(17,20)
    # on connait Text (vérité terrain) sur toute la longueur de l'épisode
    datas[:,1] = Text[pos:pos+wsize]
    #print(wsize+4*24*3600//interval)
    occupation = agenda[pos:pos+wsize+4*24*3600//interval]
    #print(occupation.shape)
    datas[:,3] = occupation[0:wsize]
    for i in range(wsize):
        datas[i,4] = getLevelDuration(occupation, i)
    # consigne
    datas[:,5] = Tc * datas[:,3]
    print("condition initiale : Qc {:.2f} Text {:.2f} Tint {:.2f}".format(datas[0,0],datas[0,1],datas[0,2]))
    return datas

def formatForNetwork(datas, index, inputs_size=inputs_size):
    """
    préparation des données pour le réseau !
    produit le state/nextstate que l'on enregistre dans la mémoire du réseau
    """
    if inputs_size == 2:
        # on donne  à l'agent les températures intérieure et extérieure à index-1
        state = np.array([datas[index-1,2], datas[index-1,1]])
    if inputs_size == 4:
        # on rajoute aux 2 paramètres précédant 2 paramètres organisationnels
        # occupation*consigne, nombre d'intervalles d'içi le changement d'occupation
        state = np.array([datas[index-1,2], datas[index-1,1], datas[index-1,5], datas[index-1,4]])

    return state

class Memory:
    """
    mémoire du réseau
    _memory : liste, contenant au maximum max_memory échantillons
    _max_memory : int
    """

    def __init__(self, max_memory):
        self._max_memory = max_memory
        self._memory = []

    def addSample(self, sample):
        """ ajout d'un échantillon à la mémoire """
        self._memory.append(sample)
        if len(self._memory) > self._max_memory:
            self._memory.pop(0)

    def samples(self, nb_samples):
        """ retourne un batch de training contenant nb_samples échantillons """
        if nb_samples > len(self._memory):
            nb_samples = len(self._memory)
        return random.sample(self._memory,nb_samples)

    def size(self):
        """ retourne la taille de la mémoire """
        return len(self._memory)

def getR1C1(datas, index):
    """
    calcule la température intérieure à l'index selon le modèle
    """
    _Qc = datas[index-1:index+1,0]
    _Text = datas[index-1:index+1,1]
    return R1C1variant(interval, R, C, _Qc, _Text, datas[index-1,2])

def getStats(datas):
    """
    stats ultra basiques (min, max, moyenne) sur vecteur datas
    """
    min = np.amin(datas)
    max = np.amax(datas)
    moy = np.mean(datas)
    return min,moy,max

def modelPlayHysteresys(datas, index=1, Tc=Tc, max_power=max_power):
    """
    le modèle joue un contrôleur hysteresys
    retourne un hash composé de :
    - un booléen indiquant s'il faut chauffer ou non
    - un tenseur de données contenant les données sources, le scénario de chauffage et la température intérieure simulée
    Tc : température intérieure de consigne
    max_power : puissance de chauffage
    """
    for i in range(index,datas.shape[0]):
        if datas[i-1,2] > Tc+hh or datas[i-1,2] < Tc-hh :
            action = datas[i-1,2] <= Tc
            datas[i,0] = action * max_power
        else:
            # on est dans la fenêtre > on ne change rien :-)
            datas[i,0] = datas[i-1,0]
        datas[i,2] = getR1C1(datas, i)

    # on vérifie si on a chauffé ou pas
    heating =  np.sum(datas[index:,0]) > 0

    return {"heating":heating, "datas":datas}

class ProgressBar:
    '''
    Visualisation temps réel de l'avancement d'un process
    '''
    def __init__ (self, valmax, title):
        if valmax == 0:  valmax = 1
        self._valmax = valmax
        self._maxbar = 30
        self._scale = float(self._maxbar / 100)
        self._title  = title

    def update(self, val):
        if val > self._valmax: val = self._valmax
        perc  = round( 100 * val / self._valmax)
        bar   = int(perc * self._scale)
        out = "\r{:20s} [{:s}{:s}] {:d}/{:d}".format(self._title,"=" * bar, " " * (self._maxbar - bar), val+1, self._valmax)
        sys.stdout.write(out)
        #Extinction du curseur
        #os.system("setterm -cursor off")
        # Rafraichissement de la barre
        sys.stdout.flush()

def saveAgent(name,suffix):
    ts = time.time()
    now = tsToHuman(ts, fmt="%Y_%m_%d_%H_%M_%S")
    if "raw" in name:
        filename = "{}_{}_{}.h5".format(name[0:-3],suffix,now)
    else:
        filename = "{}_{}_{}".format(now,suffix,name)
    agent.save(filename)
    return filename

class Training:
    """
    boite à outil de simulation pour l'entrainement du réseau neurone par renforcement
    """
    def __init__(self, name):
        self._name = name
        self._exit = False
        self._ts = int(time.time())
        # numéro de l'épisode
        self._steps = 0
        # initialisation de la mémoire de l'agent
        self._mem = Memory(MEMORY_SIZE)
        self._eps = MAX_EPS
        self._episodes_ts = []
        self._rewards = []
        self._Text = []
        self._Tint = []
        self._Tintocc = []

    def _sigint_handler(self, signal, frame):
        """
        Réception du signal de fermeture
        """
        print("signal de fermeture reçu")
        self._exit = True

    def play(self, ts=None):
        """
        """
        pos, tsvrai = setStart()
        xr = np.arange(tsvrai, tsvrai+wsize*interval, interval)
        datas = buildEnv(pos)

        result = modelPlayHysteresys(copy.deepcopy(datas))
        mConso = int(np.sum(result["datas"][1:,0]) / 1000)

        for i in range(1,wsize):
            predictionBrute = agent(formatForNetwork(datas, i).reshape(1,inputs_size))
            action = np.argmax(predictionBrute)
            datas[i,0] = action * max_power
            datas[i,2] = getR1C1(datas, i)
        aConso = int(np.sum(datas[1:,0]) / 1000)

        # matérialisation de la zone de confort par un hystéréris autour de la température de consigne
        zoneconfort = Rectangle((xr[0], Tc-hh), xr[-1]-xr[0], 2*hh, facecolor='g', alpha=0.5, edgecolor='None', label="zone de confort")
        title = "épisode {} - {} {}".format(self._steps,tsvrai, tsToHuman(tsvrai))
        title = "{}\n conso Modèle {} conso Agent {}".format(title, mConso, aConso)
        ax1 = plt.subplot(311)
        plt.title(title)
        ax1.add_patch(zoneconfort)
        plt.ylabel("Temp. intérieure °C")
        plt.plot(xr, result["datas"][:,2], color="orange", label="TintMod")
        plt.plot(xr, datas[:,2], color="black", label="TintAgent")
        plt.legend(loc='upper left')

        ax2 = ax1.twinx()
        plt.ylabel("Temp. extérieure °C")
        plt.plot(xr, result["datas"][:,1], color="blue", label="Text")
        plt.legend(loc='upper right')

        plt.subplot(312, sharex=ax1)
        plt.ylabel("Consommation W")
        plt.plot(xr, result["datas"][:,0], color="orange", label="consoMod")
        plt.plot(xr, datas[:,0], color="black", label="consoAgent")
        plt.legend()

        ax3 = plt.subplot(313, sharex=ax1)
        plt.ylabel("°C")
        plt.plot(xr, result["datas"][:,3],'o', markersize=2)
        # pas la peine d'afficher la consigne : on a la zone de confort et les zones d'occupation
        plt.plot(xr, result["datas"][:,5], label="consigne")
        plt.legend(loc='upper left')
        ax4 = ax3.twinx()
        plt.ylabel("nb intervalles > cgt occ.")
        plt.plot(xr, result["datas"][:,4],'o', markersize=1, color="red")

        plt.show()

    def trainOnce(self):
        """
        entrainement sur batch
        Q : fonction de valeur action-état, sortie du réseau neurone lorsqu'on lui donne un état
        l'action qui sera réalisée est np.argmax(Q), autrement dit on choisit l'action 0 si Q[0]>Q[1] et l'action 1 si Q[1]>Q[0]
        - extrait un batch de la mémoire
        - chaque élément du batch est de la forme (state,action,reward,nextstate)
        - calcule les valeurs de Q pour state et nextstate, pour tous les éléments du batch
        - recalcule les valeurs de Q_state[action décidée] en utilisant la régle du Q learning
        - entraine le réseau sur cette nouvelle base
        régle du Q learning, tenant compte des récompenses immédiate et différée :
        ```
        Q_state[action décidée] = récompense + GAMMA * max(Q_nextstate)
        ```
        """
        # entrainement du réseau si on a assez de données
        if not self._mem.size() > BATCH_SIZE * 3:
            return
        batch=self._mem.samples(BATCH_SIZE)
        states = np.array([val[0] for val in batch])
        nextstates = np.array([val[3] for val in batch])
        # Q learning
        # qsa : Q values for state
        # qsad : Q values for next state
        # le réseau renvoie un tableau de 2 valeurs
        # la première est la valeur de Q pour action=0
        # la seconde est la valeur de Q pour action=1
        qsa=agent(states)
        qsad=agent(nextstates)
        x=np.zeros((BATCH_SIZE,inputs_size))
        y=np.zeros((BATCH_SIZE,numAct))
        """
        b[0] : state
        b[1] : action
        b[2] : reward
        b[3] : nextstate
        mécanisme :
        qsa > reward + GAMMA (max qsad)
        max qsad > rewardd + GAMMA (max qsadd)
        qsa > reward + GAMMA rewardd + GAMMA**2 (max qsadd)
        """
        for i, b in enumerate(batch):
            q = tf.unstack(qsa[i])
            q[b[1]] = b[2] + GAMMA * np.amax(qsad[i])
            x[i] = b[0]
            y[i] = tf.stack(q)
        agent.train_on_batch(x, y)

    def train(self):
        """
        - joue un épisode
        - nourrit la mémoire
        - entraine sur batch dès que la mémoire le permet
        - met à jour le decay parameter, qui détermine la part d'aléatoire dans l'entrainement
        """
        # quant on a un bug à un épisode, on note le timestamp
        # on force ensuite le code à rejouer cet épisode
        # ex : pos, tsvrai = setStart(1601659940)
        pos, tsvrai = setStart()
        datas = buildEnv(pos)

        # l'agent joue l'épisode
        rewardTab = []
        # random predictions vs agent predictions
        rpred = 0
        apred = 0
        train = False
        if self._mem.size() > BATCH_SIZE * 3:
            barre = ProgressBar(wsize-1,"training")
            train = True
        conso = 0
        for i in range(1,wsize):
            state = formatForNetwork(datas, i)
            if random.random() < self._eps:
                rpred += 1
                action = random.randint(0, numAct - 1)
            else:
                apred += 1
                predictionBrute = agent(state.reshape(1,inputs_size))
                action = np.argmax(predictionBrute)
            conso += action
            # on exécute l'action choisir et on met à jour le tenseur de données
            datas[i,0] = action * max_power
            datas[i,2] = getR1C1(datas, i)
            nextstate = formatForNetwork(datas, i+1)
            reward = - abs(datas[i,2] - Tc)
            self._mem.addSample((state,action,reward,nextstate))
            rewardTab.append(reward)
            if train:
                self.trainOnce()
                barre.update(i-1)
            npreds = self._steps * (wsize -1) + i
            self._eps = MIN_EPS + (MAX_EPS - MIN_EPS) * math.exp(-LAMBDA * npreds)
        if train: print()
        print("épisode {} - {} aléatoires / {} réseau".format(self._steps, rpred, apred))
        Text_min, Text_moy, Text_max = getStats(datas[1:,1])
        Tint_min, Tint_moy, Tint_max = getStats(datas[1:,2])
        print("Text min {:.2f} Text moy {:.2f} Text max {:.2f}".format(Text_min, Text_moy, Text_max))
        print("Tint min {:.2f} Tint moy {:.2f} Tint max {:.2f}".format(Tint_min, Tint_moy, Tint_max))
        self._Text.append([Text_min, Text_moy, Text_max])
        self._Tint.append([Tint_min, Tint_moy, Tint_max])

        nbocc = np.sum(datas[1:,3])
        print("{} points en occupation".format(nbocc))
        if nbocc > 0 :
            #w ne contient que les valeurs de température intérieure en période d'occupation
            w = datas[datas[:,3]!=0,2]
            if w.shape[0] == 1:
                self._Tintocc.append([w[0], w[0], w[0]])
            else:
                Tocc_min, Tocc_moy, Tocc_max = getStats(w[1:])
                self._Tintocc.append([Tocc_min, Tocc_moy, Tocc_max])
            print("Tocc min {:.2f} Tocc moy {:.2f} Tocc max {:.2f}".format(self._Tintocc[-1][0], self._Tintocc[-1][1], self._Tintocc[-1][2]))
        else:
            self._Tintocc.append([None, None, None])

        rewardTab = np.array(rewardTab)
        a = np.sum(rewardTab)
        print("Récompense(s) {}".format(a))
        self._rewards.append(a)

        self._episodes_ts.append(tsvrai)


    def run(self):
        """
        boucle d'exécution
        """
        # Set signal handler to catch SIGINT or SIGTERM and shutdown gracefully
        signal.signal(signal.SIGINT, self._sigint_handler)
        signal.signal(signal.SIGTERM, self._sigint_handler)

        if not self._exit:
            pass

        # Until asked to stop
        while not self._exit:

            if MAX_EPISODES:
                if self._steps > MAX_EPISODES:
                    self._exit = True

            if mode == "play":
                self.play()
            else :
                self.train()
            self._steps += 1

            time.sleep(0.1)


    def close(self):
        """
        à la fermeture, si on vient de procéder à un entrainement :
        - on enregistre le réseau
        - on produit les graphiques qualité
        """
        if mode == "play":
            print("leaving the game")
        else:
            print("training has stopped")
            if len(self._rewards):
                self._rewards=np.array(self._rewards)
                self._Text = np.array(self._Text)
                self._Tint = np.array(self._Tint)

                name = saveAgent(self._name,"trained")

                d = int(time.time()) - self._ts

                title = "durée entrainement : {} s".format(d)

                plt.figure(figsize=(20, 10))
                ax1 = plt.subplot(211)
                plt.title(title)
                plt.plot(self._Text[:,0], color="blue")
                plt.plot(self._Text[:,1], "o", color="blue")
                plt.plot(self._Text[:,2], color="blue")
                plt.plot(self._Tint[:,0], color="orange")
                plt.plot(self._Tint[:,1], "o", color="orange")
                plt.plot(self._Tint[:,2], color="orange")
                plt.subplot(212, sharex=ax1)
                plt.plot(self._rewards)
                # enregistrement des indicateurs qualité de l'entrainement
                plt.savefig("{}".format(name[0:-3]))
                ax1.set_xlim(0, 200)
                plt.savefig("{}_begin".format(name[0:-3]))
                ax1.set_xlim(MAX_EPISODES-200, MAX_EPISODES-1)
                plt.savefig("{}_end".format(name[0:-3]))


if __name__ == "__main__":

    mode = input("train/play ?")

    readline.set_completer_delims('\t')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(simplePathCompleter)
    name = input("nom du réseau ?")
    if not name:
        name = "RLcontrol.h5"

    if ".h5" not in name:
        name = "{}.h5".format(name)

    savedModel = False
    if os.path.isfile(name):
        savedModel = True

    import tensorflow as tf

    if savedModel == True:
        agent = tf.keras.models.load_model(name)
        inlayer=agent.get_layer(name="states")
        inputs_size = inlayer.get_config()["batch_input_shape"][1]
    else :
        agent = initializeNN(inputs_size, name)
        name = saveAgent(name,"raw")
        print(name)

    visNN(agent)
    input("press a key")

    meta = getMeta(circuit["Tint"],dir)

    # durée du flux en secondes
    fullLength = meta["npoints"] * meta["interval"]
    print("Caractéristiques du flux de température extérieure")
    print("Démarrage : {}".format(meta["start_time"]))
    print("Fin: {}".format(meta["start_time"]+fullLength))
    print("Durée totale en secondes: {}".format(fullLength))

    _tss = meta["start_time"]
    _tse = meta["start_time"]+fullLength
    # mettre 1628000000 à la place de 1615000000 quand on joue avec les données de Marc Bloch

    if _tse <= _tss :
        sys.exit()

    if _tse - _tss <= wsize*interval + 4*24*3600 :
        print("Vous n'aurez pas assez de données pour travailler : impossible de poursuivre")
        sys.exit()

    length = _tse - _tss
    npoints =  length // interval
    print(tsToHuman(_tss),tsToHuman(_tse))
    print("Vous allez travailler sur une durée de {} secondes".format(length))
    print("au pas de {} secondes, le nombre de points sera de {}".format(interval,npoints))
    print("pour information, la durée d'un épisode est de {} intervalles".format(wsize))
    input("pressez une touche pour continuer")

    Text = PyFina(circuit["Text"], dir, _tss, interval, npoints)

    agenda = basicAgenda(npoints,interval, _tss,-1,-1,schedule=schedule)

    # affichage de la vérité terrain pour s'assurer qu'il n'y a pas de valeurs aberrantes
    plt.figure(figsize=(20, 10))
    ax1=plt.subplot(211)
    plt.plot(meta["start_time"]+Text.timescale(),Text, label='Text')
    plt.legend()
    ax2 = plt.subplot(212,  sharex=ax1)
    plt.plot(meta["start_time"]+Text.timescale(),agenda, label='occupation')
    plt.legend()
    plt.show()

    sandbox = Training(name)
    sandbox.run()
    sandbox.close()
    plt.close()
