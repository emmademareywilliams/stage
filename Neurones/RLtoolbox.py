
"""
reinforcement learning toolbox
"""
# nombre d'épisodes que l'on souhaite jouer
# pour jouer à l'infini, mettre MAX_EPISODES = None
# dans le cas d'un entrainement à l'infini, attention dans ce cas à la mémoire vive
# à surveiller via la commande `watch -n 1 free`
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
#   * grande valeur de LAMBDA <--> on privilégie l'exploitation
#   * petite valeur de LAMBDA <--> on privilégie l'exploration
LAMBDA = 0.001
LAMBDA = 0.0005

# discount parameter
# plus cette valeur est petite, moins on tient compte des récompenses différées
# = on donne plus d'importance aux récompenses immédiates
GAMMA = 0.9
#GAMMA = 0.05

# modèle par défault de type R1C1
modelRC = {"R": 3.08814171e-04, "C": 8.63446560e+08}


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
    Tc : température de consigne / confort temperature set point (°C)
    hh : demi-intervalle (en °C) pour le contrôle hysteresys
    TO DO : documenter la signification des autres variables d'entrée
    """
    def __init__(self, Text, agenda, tss, tse, interval, wsize, max_power, Tc, hh, **model):
        self._Text = Text
        self._agenda = agenda
        self._tss = tss
        self._tse = tse
        self._interval = interval
        self._wsize = wsize
        self._max_power = max_power
        self._Tc = Tc
        self._hh = hh
        self._model = modelRC
        if model:
            self._model = model

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
        self._pos = (ts - self._tss) // self._interval
        self._tsvrai = self._tss + self._pos * self._interval

        print("*************************************")
        print("{} - {}".format(ts,tsToHuman(ts)))
        print("vrai={} - {}".format(self._tsvrai, tsToHuman(self._tsvrai)))

    def buildEnv(self):
        """
        retourne le tenseur des données de l'épisode
        - axe 0 = le temps
        - axe 1 = les paramètres
        nombre de paramètres pour décrire l'environnement
        3 paramètres physiques : Qc, Text et Tint
        on pourrait rajouter le soleil mais le R1C1 n'en a pas besoin
        2 paramètres organisationnels :
        - temperature de consigne * occupation - si > 0 : bâtiment occupé,
        - nombre d'intervalles d'ici le changement d 'occupation, sorte de time of flight,
        """
        datas=np.zeros((self._wsize, 5))
        # condition initiale aléatoire
        datas[0,0] = random.randint(0,1)*self._max_power
        datas[0,2] = random.randint(17,20)
        # on connait Text (vérité terrain) sur toute la longueur de l'épisode
        datas[:,1] = self._Text[self._pos:self._pos+self._wsize]
        occupation = self._agenda[self._pos:self._pos+self._wsize+4*24*3600//self._interval]
        for i in range(self._wsize):
            datas[i,4] = getLevelDuration(occupation, i)
        # consigne
        datas[:,3] = self._Tc * occupation[0:self._wsize]
        print("condition initiale : Qc {:.2f} Text {:.2f} Tint {:.2f}".format(datas[0,0],datas[0,1],datas[0,2]))
        return datas

    def xr(self):
        """
        retourne le tableau des timestamps sur l'épisode et un objet pour matérialiser la zone de confort
        """
        xr = np.arange(self._tsvrai, self._tsvrai+self._wsize*self._interval, self._interval)
        Tc = self._Tc
        hh = self._hh
        zoneconfort = Rectangle((xr[0], Tc-hh), xr[-1]-xr[0], 2*hh, facecolor='g', alpha=0.5, edgecolor='None', label="zone de confort")
        return xr, zoneconfort

    def sim(self, datas, i):
        """
        simule la situation à l'étape i
        utilise içi un modèle R1C1
        peut être réécrite dans une classe fille si on veut changer de modèle
        """
        _Qc = datas[i-1:i+1,0]
        _Text = datas[i-1:i+1,1]
        #print("Text shape : {}, Qc shape : {}".format(_Text.shape[0], _Qc.shape[0]))
        return R1C1variant(self._interval, self._model["R"], self._model["C"], _Qc, _Text, datas[i-1,2])

    def sim2Target(self, datas, i):
        """
        simule la situation au prochain changement d'occupation
        utilise içi un modèle R1C1
        peut être réécrite dans une classe fille si on veut changer de modèle
        """
        tof = int(datas[i-1, 4])
        Qc = np.ones(tof)*self._max_power
        # datas[i,1] correspond à Text[i+pos]
        Text = self._Text[self._pos+i-1:self._pos+i-1+tof]
        Tint = datas[i-1, 2]
        #print("variant : Text shape : {}, Qc shape : {}, tof : {}".format(Text.shape[0], Qc.shape[0], tof))
        return R1C1sim(self._interval, self._model["R"], self._model["C"], Qc, Text, Tint)

    def play(self, datas):
        """
        à définir dans la classe fille pour jouer une stratégie de chauffe
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
        # sert uniquement pour évaluer la durée de l'entrainement
        self._ts = int(time.time())
        # numéro de l'épisode
        self._steps = 0
        # initialisation de la mémoire de l'agent
        self._mem = Memory(MEMORY_SIZE)
        self._eps = MAX_EPS
        """
        on parle de luxe si la température intérieure est supérieure à Tc+hh
        on parle d'inconfort si la température intérieure est inférieure à Tc-hh
        en mode play, les colonnes de la matrice stats sont les suivantes :
        - 0 : timestamp de l'épisode,
        - 1 à 4 : agent température intérieure moyenne, nb pts luxe, nb pts inconfort, consommation
        - 5 à 8 : modèle idem
        en mode train :
        - 0 : timestamp de l'épisode
        - 1 : récompense
        - 2 à 10 : Text min, moy et max, puis la même chose pour Tint et Tint en période d'occupation
        """
        if mode == "play":
            self._stats = np.zeros((MAX_EPISODES, 9))
        else :
            self._stats = np.zeros((MAX_EPISODES, 11))

    def getConfig(self):
        """
        extrait la configuration du réseau
        taille de l'input
        taille de la sortie
        """
        self._LNames = []
        for layer in self._agent.layers:
            self._LNames.append(layer.name)
        outputName = "output"
        if "dense_1" in self._LNames:
            outputName = "dense_1"
        outlayer = self._agent.get_layer(name=outputName)
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


    def stats(self, datas):
        w = datas[datas[:,3]!=0,2]
        inc = w[w[:] < self._env._Tc - self._env._hh]
        luxe = w[w[:] > self._env._Tc + self._env._hh]
        Tocc_moy = round(np.mean(w[:]),2)
        nbinc = inc.shape[0]
        nbluxe = luxe.shape[0]
        return Tocc_moy, nbinc, nbluxe


    def play(self, silent, ts=None):
        """
        """
        self._env.setStart(ts)
        adatas = self._env.buildEnv()
        wsize = adatas.shape[0]

        mdatas = self._env.play(copy.deepcopy(adatas))
        mConso = int(np.sum(mdatas[1:,0]) / 1000)

        for i in range(1,wsize):
            if "dense_1" in self._LNames :
                # on permute Tint et Text car les agents jusque début 2021 prenaient Tint en premier....
                # on pourrait utiliser np.array([ adatas[i-1,2], adatas[i-1,1], adatas[i-1,3], adatas[i-1,4] ])
                # mais le slicing donne un code plus lisible et plus court :-)
                state = adatas[i-1, [2,1,3,4] ]
            else:
                state = adatas[i-1, 1:self._inSize + 1]
            predictionBrute = self._agent(state.reshape(1, self._inSize))
            action = np.argmax(predictionBrute)
            adatas[i,0] = action * self._env._max_power
            adatas[i,2] = self._env.sim(adatas, i)
        aConso = int(np.sum(adatas[1:,0]) / 1000)

        aTocc_moy, aNbinc, aNbluxe = self.stats(adatas[1:,:])
        mTocc_moy, mNbinc, mNbluxe = self.stats(mdatas[1:,:])
        line = np.array([self._env._tsvrai, aTocc_moy, aNbluxe, aNbinc, aConso, mTocc_moy, mNbluxe, mNbinc, mConso])
        #print(line)
        self._stats[self._steps, :] = line

        if not silent:
            xr, zoneconfort = self._env.xr()
            title = "épisode {} - {} {}".format(self._steps, self._env._tsvrai, tsToHuman(self._env._tsvrai))
            title = "{}\n conso Modèle {} Agent {}".format(title, mConso, aConso)
            title = "{}\n Tocc moyenne modèle : {} agent : {}".format(title, mTocc_moy, aTocc_moy)
            title = "{}\n nb heures inconfort modèle : {} agent : {}".format(title, mNbinc, aNbinc)

            ax1 = plt.subplot(311)
            plt.title(title, fontsize=8)
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
        fonction récompense
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
        # ex : self.setStart(1601659940)
        self._env.setStart()
        adatas = self._env.buildEnv()
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
            adatas[i,0] = action * self._env._max_power
            adatas[i,2] = self._env.sim(adatas, i)
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
        if train: print() # retour chariot pour changer d'épisode
        print("épisode {} - {} aléatoires / {} réseau".format(self._steps, rpred, apred))
        Text_min, Text_moy, Text_max = getStats(adatas[1:,1])
        Tint_min, Tint_moy, Tint_max = getStats(adatas[1:,2])
        print("Text min {:.2f} Text moy {:.2f} Text max {:.2f}".format(Text_min, Text_moy, Text_max))
        print("Tint min {:.2f} Tint moy {:.2f} Tint max {:.2f}".format(Tint_min, Tint_moy, Tint_max))
        self._stats[self._steps, 2:8] = np.array([Text_min, Text_moy, Text_max, Tint_min, Tint_moy, Tint_max])

        if np.sum(adatas[1:,3]) > 0 :
            #w ne contient que les valeurs de température intérieure en période d'occupation
            w = adatas[adatas[:,3]!=0,2]
            print("{} points en occupation".format(w.shape[0]))
            if w.shape[0] == 1:
                self._stats[self._steps, 8:] = np.array([w[0], w[0], w[0]])
                print("Tocc {:.2f}".format(w[0]))
            else:
                Tocc_min, Tocc_moy, Tocc_max = getStats(w[1:])
                self._stats[self._steps, 8:] = np.array([Tocc_min, Tocc_moy, Tocc_max])
                print("Tocc min {:.2f} Tocc moy {:.2f} Tocc max {:.2f}".format(Tocc_min, Tocc_moy, Tocc_max))
        else:
            self._stats[self._steps, 8:] = np.array([None, None, None])

        rewardTab = np.array(rewardTab)
        a = np.sum(rewardTab)
        self._stats[self._steps, :2] = np.array([self._env._tsvrai, a])
        print("Récompense(s) {}".format(a))


    def run(self, silent=False):
        """
        boucle d'exécution
        """
        # Set signal handler to catch SIGINT or SIGTERM and shutdown gracefully
        signal.signal(signal.SIGINT, self._sigint_handler)
        signal.signal(signal.SIGTERM, self._sigint_handler)

        # Until asked to stop
        while not self._exit:
            if MAX_EPISODES:
                if self._steps >= MAX_EPISODES-1:
                    self._exit = True

            if self._mode == "play":
                self.play(silent=silent)
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

            title = "nombre d'épisodes joués : {} \n".format(self._steps)
            aConsoMoy = round(np.mean(self._stats[:,4]),0)
            mConsoMoy = round(np.mean(self._stats[:,8]),0)
            title = "{} Conso moyenne agent : {} / Conso moyenne modèle : {} \n".format(title, aConsoMoy, mConsoMoy)

            pct = round(100*(mConsoMoy-aConsoMoy)/mConsoMoy, 2)
            title = "{} Pourcentage de gain agent : {} %".format(title, pct)

            plt.figure(figsize=(20, 10))
            ax1 = plt.subplot(311)
            plt.title(title)
            plt.plot(self._stats[:,1], color="blue", label='température moyenne occupation agent')
            plt.plot(self._stats[:,5], color="red", label='température moyenne occupation modèle')
            plt.legend()

            ax2 = plt.subplot(312, sharex=ax1)
            plt.plot(self._stats[:,2], color="blue", label="nombre heures > {}°C agent".format(self._env._Tc + self._env._hh))
            plt.plot(self._stats[:,6], color="red", label="nombre heures > {}°C modèle".format(self._env._Tc + self._env._hh))
            plt.legend()

            ax3 = plt.subplot(313, sharex=ax1)
            plt.plot(self._stats[:,3], color="blue", label="nombre heures < {}°C agent".format(self._env._Tc - self._env._hh))
            plt.plot(self._stats[:,7], color="red", label="nombre heures < {}°C modèle".format(self._env._Tc - self._env._hh))
            plt.legend()
            plt.show()

        else:
            print("training has stopped")

            name = saveNN(self._agent, self._name, "trained")

            d = int(time.time()) - self._ts

            title = "durée entrainement : {} s".format(d)

            plt.figure(figsize=(20, 10))
            ax1 = plt.subplot(211)
            plt.title(title)

            colors = ["blue", "orange", "green"]
            for i in range(9):
                j = i // 3
                if i % 3 == 1:
                    plt.plot(self._stats[:,i+2], "o", color=colors[j])
                else :
                    plt.plot(self._stats[:,i+2], color=colors[j])

            plt.subplot(212, sharex=ax1)
            plt.plot(self._stats[:,1])
            # enregistrement des indicateurs qualité de l'entrainement
            plt.savefig("{}".format(name[0:-3]))
            ax1.set_xlim(0, 200)
            plt.savefig("{}_begin".format(name[0:-3]))
            ax1.set_xlim(MAX_EPISODES-200, MAX_EPISODES-1)
            plt.savefig("{}_end".format(name[0:-3]))
            header = "ts,reward"
            for t in ["Text","Tint","Tintocc"]:
                header = "{0},{1}_min,{1}_moy,{1}_max".format(header,t)
            np.savetxt('{}.csv'.format(name[0:-3]), self._stats, delimiter=',', header=header)
        plt.close()
