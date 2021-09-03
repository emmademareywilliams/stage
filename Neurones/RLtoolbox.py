
"""
reinforcement learning toolbox
"""
# nombre d'épisodes que l'on souhaite jouer
# pour jouer à l'infini, mettre MAX_EPISODES = None
# dans le cas d'un entrainement à l'infini, attention dans ce cas à la mémoire vive
# à surveiller via la commande free
MAX_EPISODES = 400

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
#   * grande valeur de LAMBDA <--> on privilégie l'exploitation
#   * petite valeur de LAMBDA <--> on privilégie l'exploration
LAMBDA = 0.001
LAMBDA = 0.0005

# discount parameter
# plus cette valeur est petite, moins on tient compte des récompenses différées
# = on donne plus d'importance aux récompenses immédiates
GAMMA = 0.9
#GAMMA = 0.05

Cw = 1162.5 #Wh/m3/K
# flow_rate en m3/h
flow_rate = 5
max_power = flow_rate * Cw * 15

# température de consigne en °C
# confort temperature set point
Tc = 20

# le modèle qui va décrire l'évolution de la température intérieure
# un modèle électrique équivalent de type R1C1
R = 3.08814171e-04
C = 8.63446560e+08

# autre test de robustesse sur les valeurs de R et de C :
R = 3.42506838e-04
C = 1.06209090e+09

# demi-intervalle (en °C) pour le contrôle hysteresys
hh = 1

import numpy as np
import tensorflow as tf
import sys
import matplotlib.pylab as plt
from matplotlib.patches import Rectangle
from planning import tsToHuman, getRandomStart, getLevelDuration
import random
import signal
import time
import copy
import math
from models import R1C1variant, R1C1sim

# pour l'autocompletion en ligne de commande
import readline
import glob

def simplePathCompleter(text,state):
    """
    tab completer pour les noms de fichiers, chemins....
    """
    line   = readline.get_line_buffer().split()

    return [x for x in glob.glob(text+'*')][state]

def initializeNN(inSize, outSize, name):
    """
    initialisation du réseau neurone qui jouera le rôle de contrôleur ou agent énergétique
    son rôle est de produire l'action énergétique (chauffage On ou Off)
    La détermination de Tint après application de cette action est faite :
    - soit par le modèle par calcul
    - soit par l'environnement réel par monitoring
    """
    tf.keras.backend.set_floatx('float32')
    inputs = tf.keras.Input(shape=(inSize, ), name='states')
    x = tf.keras.layers.Dense((50), activation='relu')(inputs)
    # pour ajouter de la profondeur (pas utilisé pour l'instant)
    #x = tf.keras.layers.Dense((50), activation='relu')(x)
    outputs = tf.keras.layers.Dense(outSize, activation='linear', name='output')(x)
    agent = tf.keras.Model(inputs=inputs, outputs=outputs, name=name)
    agent.compile(loss="mse", optimizer="adam", metrics=['mae'])
    print("initialisation de l'agent terminée")
    return agent

def visNN(agent):
    """
    visualisation des poids du réseau
    """
    agent.summary()
    #print(agent.get_weights())

def saveNN(agent, name, suffix):
    """
    sauve le réseau au format h5
    """
    ts = time.time()
    now = tsToHuman(ts, fmt="%Y_%m_%d_%H_%M_%S")
    if "raw" in name:
        filename = "{}_{}_{}.h5".format(name[0:-3],suffix,now)
    else:
        filename = "{}_{}_{}".format(now,suffix,name)
    agent.save(filename)
    return filename

class Environnement:
    """
    stocke les données décrivant l'environnement et offre des méthodes pour le caractériser
    """
    def __init__(self, Text, agenda, tss, tse, interval, wsize):
        self._Text = Text
        self._agenda = agenda
        self._tss = tss
        self._tse = tse
        self._interval = interval
        self._wsize = wsize

    def setStart(self, ts=None):
        """
        tire un timestamp aléatoirement avant fin mai OU après début octobre
        ou le fixe à une valeur donnée,si ts est fourni, pour rejouer un épisode (ex : 1588701000)

        retourne la position dans la timeserie et le timestamp correspondant
        """
        if ts is None:
            start = self._tss
            end = self._tse - self._wsize * self._interval - 4*24*3600
            #print(tsToHuman(start),tsToHuman(end))
            # on tire un timestamp avant fin mai OU après début octobre
            ts = getRandomStart(start, end, 10, 5)
        pos = (ts - self._tss) // self._interval
        tsvrai = self._tss + pos * self._interval

        print("*************************************")
        print("{} - {}".format(ts,tsToHuman(ts)))
        print("vrai={} - {}".format(tsvrai, tsToHuman(tsvrai)))
        return pos, tsvrai

    def buildEnv(self, pos):
        """
        retourne le tenseur des données de l'épisode
        - axe 0 = le temps
        - axe 1 = les paramètres
        nombre de paramètres pour décrire l'environnement
        3 paramètres physiques : Qc, Text et Tint
        dans la vraie vie, on pourrait rajouter le soleil mais le R1C1 n'en a pas besoin
        2 paramètres organisationnels :
        - temperature de consigne * occupation - si > 0 : bâtiment occupé,
        - nombre d'intervalles d'ici le changement d 'occupation, sorte de time of flight,
        """
        datas=np.zeros((self._wsize, 5))
        # condition initiale aléatoire
        datas[0,0] = random.randint(0,1)*max_power
        datas[0,2] = random.randint(17,20)
        # on connait Text (vérité terrain) sur toute la longueur de l'épisode
        datas[:,1] = self._Text[pos:pos+self._wsize]
        occupation = self._agenda[pos:pos+self._wsize+4*24*3600//self._interval]
        for i in range(self._wsize):
            datas[i,4] = getLevelDuration(occupation, i)
        # consigne
        datas[:,3] = Tc * occupation[0:self._wsize]
        print("condition initiale : Qc {:.2f} Text {:.2f} Tint {:.2f}".format(datas[0,0],datas[0,1],datas[0,2]))
        return datas

    def xr(self, tsvrai):
        """
        retourne le tableau des timestamps sur l'épisode
        """
        return np.arange(tsvrai, tsvrai+self._wsize*self._interval, self._interval)

    def getR1C1(self, datas, index):
        """
        calcule la température intérieure à l'index selon un modèle R1C1
        """
        _Qc = datas[index-1:index+1,0]
        _Text = datas[index-1:index+1,1]
        #print("Text shape : {}, Qc shape : {}".format(_Text.shape[0], _Qc.shape[0]))
        return R1C1variant(self._interval, R, C, _Qc, _Text, datas[index-1,2])

    def getR1C1variant(self, datas, index, pos, tof):
        """
        calcul de température par convolution
        utilisé dans le modèle avec occupation
        """
        Qc = np.ones(tof)*max_power
        # datas[i,1] correspond à Text[i+pos]
        Text = self._Text[pos+index-1:pos+index-1+tof]
        Tint = datas[index-1, 2]
        #print("variant : Text shape : {}, Qc shape : {}, tof : {}".format(Text.shape[0], Qc.shape[0], tof))
        return R1C1sim(self._interval, R, C, Qc, Text, Tint)

    def play(self, datas):
        """
        à définir dans la classe fille
        retourne le tenseur de données sources complété par le scénario de chauffage et la température intérieure simulée
        """
        return datas

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

def getStats(datas):
    """
    stats ultra basiques (min, max, moyenne) sur vecteur datas
    """
    min = np.amin(datas)
    max = np.amax(datas)
    moy = np.mean(datas)
    return min,moy,max

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
        # Rafraichissement de la barre
        sys.stdout.flush()

class Training:
    """
    boite à outil de simulation pour l'entrainement du réseau neurone par renforcement
    """
    def __init__(self, name, mode, env, agent):
        self._name = name
        self._mode = mode
        self._env = env
        self._agent = agent
        self.getConfig()
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

    def getConfig(self):
        """
        extrait la configuration du réseau
        taille de l'input
        taille de la sortie
        """
        outlayer = self._agent.get_layer(name="output")
        inlayer = self._agent.get_layer(name="states")
        self._outSize = outlayer.get_config()['units']
        self._inSize = inlayer.get_config()["batch_input_shape"][1]
        print("network input size {} output size {}".format(self._inSize, self._outSize))

    def _sigint_handler(self, signal, frame):
        """
        Réception du signal de fermeture
        """
        print("signal de fermeture reçu")
        self._exit = True


    def stats(self, datas, wsize):
        Tocc = []
        inc = 0
        for i in range(1, wsize):
            if datas[i, 3] != 0:
                # si on est en période d'occupation
                Tocc.append(datas[i, 2])
                if datas[i, 2] < Tc-hh or datas[i, 2] > Tc+hh:
                    # cas d'un intervalle d'inconfort
                    inc += 1

        Tocc_moy = round(np.mean(Tocc),2)
        incHour = inc*self._env._interval //3600
        return incHour, Tocc_moy


    def play(self, ts=None):
        """
        """
        pos, tsvrai = self._env.setStart(ts)
        xr = self._env.xr(tsvrai)
        adatas = self._env.buildEnv(pos)
        wsize = adatas.shape[0]

        mdatas = self._env.play(copy.deepcopy(adatas), pos)
        mConso = int(np.sum(mdatas[1:,0]) / 1000)

        for i in range(1,wsize):
            state = adatas[i-1, 1:self._inSize + 1]
            predictionBrute = self._agent(state.reshape(1, self._inSize))
            action = np.argmax(predictionBrute)
            adatas[i,0] = action * max_power
            adatas[i,2] = self._env.getR1C1(adatas, i)
        aConso = int(np.sum(adatas[1:,0]) / 1000)

        aIncHour, aTocc_moy = self.stats(adatas, wsize)
        mIncHour, mTocc_moy = self.stats(mdatas, wsize)

        # matérialisation de la zone de confort par un hystéréris autour de la température de consigne
        zoneconfort = Rectangle((xr[0], Tc-hh), xr[-1]-xr[0], 2*hh, facecolor='g', alpha=0.5, edgecolor='None', label="zone de confort")

        title = "épisode {} - {} {}".format(self._steps, tsvrai, tsToHuman(tsvrai))
        title = "{}\n conso Modèle {} conso Agent {}".format(title, mConso, aConso)
        title = "{}\n Tocc moyenne modèle : {} agent : {} \n nb heures inconfort modèle : {} agent : {}".format(title, mTocc_moy, aTocc_moy, mIncHour, aIncHour)

        ax1 = plt.subplot(311)
        plt.title(title)
        ax1.add_patch(zoneconfort)
        plt.ylabel("Temp. intérieure °C")
        plt.plot(xr, mdatas[:,2], color="orange", label="TintMod")
        plt.plot(xr, adatas[:,2], color="black", label="TintAgent")
        plt.legend(loc='upper left')

        ax2 = ax1.twinx()
        plt.ylabel("Temp. extérieure °C")
        plt.plot(xr, mdatas[:,1], color="blue", label="Text")
        plt.legend(loc='upper right')

        plt.subplot(312, sharex=ax1)
        plt.ylabel("Consommation W")
        plt.plot(xr, mdatas[:,0], color="orange", label="consoMod")
        plt.plot(xr, adatas[:,0], color="black", label="consoAgent")
        plt.legend()

        ax3 = plt.subplot(313, sharex=ax1)
        plt.ylabel("°C")
        plt.plot(xr, mdatas[:,3], label="consigne")
        plt.legend(loc='upper left')
        ax4 = ax3.twinx()
        plt.ylabel("nb intervalles > cgt occ.")
        plt.plot(xr, mdatas[:,4],'o', markersize=1, color="red")

        plt.show()

    def reward(self, datas, i):
        """
        à définir dans la classe fille
        """
        return 0

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
        qsa=self._agent(states)
        qsad=self._agent(nextstates)
        x=np.zeros((BATCH_SIZE, self._inSize))
        y=np.zeros((BATCH_SIZE, self._outSize))
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
        self._agent.train_on_batch(x, y)

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
        pos, tsvrai = self._env.setStart()
        adatas = self._env.buildEnv(pos)
        wsize = adatas.shape[0]

        # l'agent joue l'épisode
        rewardTab = []
        # random predictions vs agent predictions
        rpred = 0
        apred = 0
        train = False
        if self._mem.size() > BATCH_SIZE * 3:
            barre = ProgressBar(wsize-1,"training")
            train = True
        for i in range(1,wsize):
            state = adatas[i-1, 1:self._inSize + 1]
            if random.random() < self._eps:
                rpred += 1
                action = random.randint(0, self._outSize - 1)
            else:
                apred += 1
                predictionBrute = self._agent(state.reshape(1, self._inSize))
                action = np.argmax(predictionBrute)
            # on exécute l'action choisir et on met à jour le tenseur de données
            adatas[i,0] = action * max_power
            adatas[i,2] = self._env.getR1C1(adatas, i)
            nextstate = adatas[i, 1:self._inSize + 1]
            # calcul de la récompense ******************************************
            reward = self.reward(adatas, i)
            self._mem.addSample((state,action,reward,nextstate))
            rewardTab.append(reward)
            if train:
                self.trainOnce()
                barre.update(i-1)
            npreds = self._steps * (wsize -1) + i
            self._eps = MIN_EPS + (MAX_EPS - MIN_EPS) * math.exp(-LAMBDA * npreds)
        if train: print()
        print("épisode {} - {} aléatoires / {} réseau".format(self._steps, rpred, apred))
        Text_min, Text_moy, Text_max = getStats(adatas[1:,1])
        Tint_min, Tint_moy, Tint_max = getStats(adatas[1:,2])
        print("Text min {:.2f} Text moy {:.2f} Text max {:.2f}".format(Text_min, Text_moy, Text_max))
        print("Tint min {:.2f} Tint moy {:.2f} Tint max {:.2f}".format(Tint_min, Tint_moy, Tint_max))
        self._Text.append([Text_min, Text_moy, Text_max])
        self._Tint.append([Tint_min, Tint_moy, Tint_max])

        if np.sum(adatas[1:,3]) > 0 :
            #w ne contient que les valeurs de température intérieure en période d'occupation
            w = adatas[adatas[:,3]!=0,2]
            print("{} points en occupation".format(w.shape[0]))
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

        # Until asked to stop
        while not self._exit:
            if MAX_EPISODES:
                if self._steps > MAX_EPISODES:
                    self._exit = True

            if self._mode == "play":
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
        if self._mode == "play":
            print("leaving the game")
        else:
            print("training has stopped")
            if len(self._rewards):
                self._rewards=np.array(self._rewards)
                self._Text = np.array(self._Text)
                self._Tint = np.array(self._Tint)
                self._Tintocc = np.array(self._Tintocc)

                name = saveNN(self._agent, self._name, "trained")

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
                plt.plot(self._Tintocc[:,0], color="green")
                plt.plot(self._Tintocc[:,1], "o", color="green")
                plt.plot(self._Tintocc[:,2], color="green")
                plt.subplot(212, sharex=ax1)
                plt.plot(self._rewards)
                # enregistrement des indicateurs qualité de l'entrainement
                plt.savefig("{}".format(name[0:-3]))
                ax1.set_xlim(0, 200)
                plt.savefig("{}_begin".format(name[0:-3]))
                ax1.set_xlim(MAX_EPISODES-200, MAX_EPISODES-1)
                plt.savefig("{}_end".format(name[0:-3]))
