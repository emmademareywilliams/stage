#!/usr/bin/env python3
"""
reinforcement learning SANDBOX

**a toolkit to train a free-model controler on a R1C1 model**
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

graphe = True
verbose = False
# non utilisé - pourrait servir à applatir un historique de plusieurs paramètres (tenseur > vecteur)
# si d est le tenseur > d.flatten(flattenOrder)
# ce type d'applatissement est dit de type Fortran
flattenOrder = "F"

dir = "/var/opt/emoncms/phpfina"

# sampling interval in seconds
interval = 3600
#interval = 900
"""
schedule = np.array([ [7,17], [7,17], [7,17], [7,17], [7,17], [-1,-1], [-1,-1] ])
"""

# DONNEES DU COLLEGE MARC BLOCH :
# flow_rate en m3/h
# numéro de flux sur le serveur local synchronisé avec le serveur de terrain via le module sync
circuit = {"name":"Nord", "Text":9, "Tint":29, "flow_rate":5, "pompe":28, "Tdep":10, "Tret":11}
# numéro de flux sur le serveur de terrain
"""
on ne peut pas utiliser themis dans le cas de CMB car on n'a pas de flux de chauffage
themis = {"name":"Nord", "Text":18, "Tint":56, "flow_rate":5.19, "pompe":26, "Tdep":25, "Tret":29}
"""
Cw = 1162.5 #Wh/m3/K
max_power = circuit["flow_rate"] * Cw * 15
# la loi d'eau du circuit
coeffs = np.array([[-10,20],
                   [85 ,40]])

# température de consigne en °C
# confort temperature set point
Tc = 20
# entrainement sur température de consigne variable ?
# non fonctionnel
randomTc = False

# le modèle qui va décrire l'évolution de la température intérieure
# un modèle électrique équivalent de type R1C1
# params empile divers jeux de paramètres représentant divers fonctionnements de circuits
# ligne 0 : circuit Nord, simulation sur 20 jours le 20 février
# ligne 1 : circuit Nord, simulation sur 20 jours le 4 mars
# ligne 2 : circuit Nord, simulation sur 10 jours le 20 février
params = np.array([[3.08814171e-04, 8.63446560e+08],
                   [3.19412465e-04,	8.87378799e+08],
                   [2.64850632e-04, 3.99920238e+08]])
i = 0
R = params[i,0]
C = params[i,1]

# demi-intervalle (en °C) pour le contrôle hysteresys
hh = 1

# Définition de la fenêtre caractérisant l'environnement
# taille de l'historique en nombre d'intervalles
history = 12*3600//interval

# nombre de paramètres pour décrire l'environnement
# 3 paramètres physiques : Qc, Text et Tint
# dans la vrai vie, on pourrait rajouter le soleil mais le R1C1 n'en a pas besoin
# 3 paramètres organisationnels :
# - occupation O/N,
# - nombre d'intervalles d'ici le changement d 'occupation, sorte de time of flight,
# - température de consigne
numPar = 6
# nombre d'actions possibles  : 2 = on chauffe ou pas
# pour l'instant, on reste simple
numAct = 2

# nombre d'intervalles sur lequel la simulation sera menée
# 60 correspond à un weekend
goto = 60*3600//interval
goto = 8*24*3600//interval

# taille de la fenêtre
wsize = history + goto + 1

# si playWithModel vaut 1, on compare le réseau au modèle sur lequel on l'a entrainé
# si playWithModel vaut 0, on compare à une stratégie de chauffe classique (réduits de nuit/week-end)
playWithModel = 1

# nombre de paramètres à fournir au réseau pour prédire l'état suivant à partir de l'état actuel
# cas 1 : on se limite à lui donner Tint[-1], Text[0]
inputs_size = 2
# cas 2 : on fournit au réseau Tint[-1], Text[0], Tc*occupation[0], tof[0]
# tof représente le nombre d'intervalles d'içi le changement d'occupation
# Tc est la température de consigne
inputs_size = 4


import os
import sys
import matplotlib.pylab as plt
from matplotlib.patches import Rectangle
import random
import signal
import time
import planning

import copy

import math

from models import R1C1sim, R1C1variant
from dataengines import PyFina, getMeta

# pour l'autocompletion en ligne de commande
import readline
import glob


def buildEnv(pos, wsize = wsize):
    """
    construit l'environnement d'un épisode sur la base d'une position donnée pos

    wsize : longueur de la fenêtre de données en nombre d'intervalles

    retourne le tenseur des données datas

    - axe 0 = le temps
    - axe 1 = les paramètres

    param. physiques : puissance de chauffage puis temp. extérieure et intérieure

    param. organisationnels : occupation, nombre d'intervalles d'içi le changement d'occupation, temp. de consigne*occupation
    """
    datas=np.zeros((wsize, numPar))
    datas[0:history,0] = Qc[pos:pos+history]
    # on connait Text (vérité terrain) sur toute la longueur de l'épisode
    datas[:,1] = Text[pos:pos+wsize]
    if numPar == 6:
        #print(wsize+4*24*3600//interval)
        occupation = agenda[pos:pos+wsize+4*24*3600//interval]
        #print(occupation.shape)
        datas[:,3] = occupation[0:wsize]
        for i in range(wsize):
            datas[i,4] = getLevelDuration(occupation, i)
        # consigne * occupation
        datas[:,5] = Tc * datas[:,3]
    # on simule la température intérieure sur l'historique
    # condition initiale pour la simulation = Tint[pos]
    # Tint température intérieure mesurée
    datas[0:history,2] = R1C1sim(interval, R, C, datas[0:history,0], datas[0:history,1], Tint[pos])
    return datas

def formatForNetwork(datas, index, inputs_size=inputs_size):
    """
    préparation des données pour le réseau !

    produit le state/nextstate que l'on enregistre dans la mémoire du réseau
    """
    if inputs_size == 2:
        # on ne conserve que :
        # - la température intérieure à index-1
        # - la température extérieure à index
        state = np.array([datas[index-1,2], datas[index,1]])
    elif inputs_size == 4:
        # on rajoute aux 2 paramètres précédant 2 paramètres organisationnels
        # occupation*consigne, nombre d'intervalles d'içi le changement d'occupation
        state = np.array([datas[index-1,2], datas[index,1], datas[index,5], datas[index,4]])
    elif inputs_size == 5:
        # on différentie température de consigne et occupation
        state = np.array([datas[index-1,2], datas[index,1], datas[index,3], datas[index,4], datas[index,5]])

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


def modelPlayHysteresys(datas, index, Tc, max_power):
    """
    le modèle joue un contrôleur hysteresys

    retourne un hash composé de :

    - un booléen indiquant s'il faut chauffer ou non
    - un tenseur de données contenant les données sources, le scénario de chauffage et la température intérieure simulée

    Tc : température intérieure de consigne

    max_power : puissance de chauffage
    """
    # on regarde ce qu'il se passe sans chauffage
    datas[index:,2] = R1C1sim(interval, R, C, datas[index:,0], datas[index:,1], datas[index-1,2])
    # s'il n'est pas nécessaire de chauffer, on peut s'arrêter là :-)
    heating = False
    if datas[-1,2] < Tc:
        heating = True
        for i in range(index,datas.shape[0]):
            if datas[i-1,2] > Tc+hh or datas[i-1,2] < Tc-hh :
                action = datas[i-1,2] <= Tc
                datas[i,0] = action * max_power
            else:
                # on est dans la fenêtre > on ne change rien :-)
                datas[i,0] = datas[i-1,0]
            datas[i,2] = getR1C1(datas, i)

    return {"heating":heating, "datas":datas}



class Training:
    """
    boite à outil de simulation pour l'entrainement du réseau neurone par renforcement
    """
    def __init__(self, step):
        self._step = step
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

    def _sigint_handler(self, signal, frame):
        """
        Réception du signal de fermeture
        """
        print("signal de fermeture reçu")
        self._exit = True

    def play(self, ts=None):
        """
        fait simplement jouer un réseau de neurone aléatoire ou pré-enregistré

        compare avec le résultat du modèle ou d'une stratégie industrielle

        calcule l'énergie consommée pour le réseau et le modèle
        """
        pos, tsvrai = setStart(ts=ts)
        xr = np.arange(tsvrai, tsvrai+(history+goto)*interval, interval)
        datas = buildEnv(pos)

        labelAgent = "agent IA"
        if playWithModel == 1:
            # le modèle joue l'épisode et produit son scénario
            #result = modelPlayNonOccupation(copy.deepcopy(datas), history, Tc, max_power)
            #result = modelPlayHysteresys(copy.deepcopy(datas), history, Tc, max_power)
            result = modelPlayWeekInHysteresys(copy.deepcopy(datas), history, Tc, max_power, pos)
            labelModel = "modèle"
        else:
            #result = industryPlayReductions(copy.deepcopy(datas), history)
            result = industryPlayHystNRed(copy.deepcopy(datas), history)
            labelModel = "réduits nuit/week-end"
        mConso = int(np.sum(result["datas"][history:,0]) / 1000)

        # l'agent joue l'épisode
        for i in range(goto):
            index = history+i
            if lite:
                predictionBrute = tflite_output(agent, formatForNetwork(datas, index))
            else:
                predictionBrute = agent(formatForNetwork(datas, index).reshape(1,inputs_size))
            action = np.argmax(predictionBrute)
            datas[index,0] = action * max_power
            datas[index,2] = getR1C1(datas, index)
        aConso = int(np.sum(datas[history:,0]) / 1000)

        title = "épisode {} - {} {}".format(self._steps,tsvrai, tsToHuman(tsvrai))
        title = "{}\n conso {} {}".format(title, labelAgent, aConso)
        if result["heating"]:
            title = "{}\n conso {} {}".format(title, labelModel, mConso)
            if "index" in result:
                title = "{} indice {}".format(title,result["index"])
            if "success" in result and not result["success"]:
                title = "{}\n consigne non atteinte : besoin de plus de puissance ".format(title)
        else:
            title = "{}\n modèle - chauffage pas nécessaire".format(title)

        nb = 211
        if datas.shape[1] >= 5 or playWithModel == 0 :
            nb = 311

        # matérialisation de la zone de confort par un hystéréris de 2 degrés autour de la température de consigne
        zoneconfort = Rectangle((xr[0], Tc-1), xr[-1]-xr[0], 2, facecolor='g', alpha=0.5, edgecolor='None', label="zone de confort")
        Tint = np.array([datas[:-1,2],result["datas"][:-1,2]])
        Tintmin = np.amin(Tint)
        Tintmax = np.amax(Tint)
        Textmin = np.amin(datas[:-1,1])
        Textmax = np.amax(datas[:-1,1])

        if datas.shape[1] >= 5:
            # on extrait tous les indices pour lesquels datas[:,4] prend sa valeur minimale = 0
            # le vecteur résultant compilera les indices indiquant un changement d'occupation
            changes = np.where(datas[:,4] == datas[:,4].min())[0]
            zonesOcc=[]
            zonesOccText=[]
            #print(changes)
            for i in changes:
                if datas[i,3] == 0:
                    imin = i
                    break
            for i in changes:
                if datas[i,3] == 0:
                    if i < datas.shape[0]-1:
                        l = datas[i+1,4]
                        h = Tintmax - Tintmin
                        w = l*interval
                        #print("{} vs {}".format(i,imin))
                        v = Rectangle((xr[i],Tintmin), w, h, facecolor='orange', alpha=0.5, edgecolor='None')
                        zonesOcc.append(v)
                        h = Textmax - Textmin
                        if i == imin:
                            v = Rectangle((xr[i],Textmin), w, h, facecolor='orange', alpha=0.5, edgecolor='None', label="occupation")
                        else:
                            v = Rectangle((xr[i],Textmin), w, h, facecolor='orange', alpha=0.5, edgecolor='None')
                        zonesOccText.append(v)

        ax1 = plt.subplot(nb)
        plt.title(title)
        ax1.add_patch(zoneconfort)
        if datas.shape[1] >= 5:
            for v in zonesOcc:
                ax1.add_patch(v)
        plt.ylabel("Temp. intérieure °C")
        #plt.plot(xr,Tint[pos:pos+history+goto], color="yellow")
        plt.plot(xr,datas[:-1,2], color="black", label="Tint {}".format(labelAgent))
        plt.plot(xr,result["datas"][:-1,2], color="orange", label="Tint {}".format(labelModel))
        plt.legend(loc='upper left')
        if playWithModel == 1:
            ax2 = ax1.twinx()
        else :
            nb += 1
            ax2=plt.subplot(nb, sharex=ax1)
            if datas.shape[1] >= 5:
                for v in zonesOccText:
                    ax2.add_patch(v)

        plt.ylabel("Temp. extérieure °C")
        plt.plot(xr,datas[:-1,1], color="blue", label="Text")
        plt.legend(loc='upper right')
        nb += 1
        plt.subplot(nb, sharex=ax1)
        #plt.plot(xr,QcTrue[pos:pos+history+goto], color="#f9acac")
        plt.ylabel("Consommation W")
        plt.plot(xr,result["datas"][:-1,0], color="orange", label=labelModel)
        plt.plot(xr, datas[:-1,0], color="black", label=labelAgent)
        plt.legend()
        if datas.shape[1] >= 5 and playWithModel == 1:
            nb+=1
            ax3 = plt.subplot(nb, sharex=ax1)
            plt.ylabel("°C")
            plt.plot(xr,datas[:-1,3],'o', markersize=2)
            # pas la peine d'afficher la consigne : on a la zone de confort et les zones d'occupation
            plt.plot(xr,datas[:-1,5], label="consigne")
            plt.legend(loc='upper left')
            ax4 = ax3.twinx()
            plt.ylabel("nb intervalles > cgt occ.")
            plt.plot(xr,datas[:-1,4],'o', markersize=1, color="red")
        plt.xlabel("Temps en secondes")
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

    def realtrain(self):
        """
        entrainement sur données réelles

        pas implémenté
        """
        pass

    def train(self):
        """
        - joue un épisode
        - nourrit la mémoire
        - entraine sur batch dès que la mémoire le permet
        - met à jour le decay parameter, qui détermine la part d'aléatoire dans l'entrainement

        """
        pos, tsvrai = setStart()
        datas = buildEnv(pos)

        # l'agent joue l'épisode
        rewardTab = []
        # random predictions vs agent predictions
        rpred = 0
        apred = 0
        train = False
        if self._mem.size() > BATCH_SIZE * 3:
            if args.cloud == 0:
                barre = ProgressBar(goto,"training")
            train = True
        conso = 0
        for i in range(goto):
            index = history+i
            state = formatForNetwork(datas, index)
            if random.random() < self._eps:
                rpred += 1
                action = random.randint(0, numAct - 1)
            else:
                apred += 1
                predictionBrute = agent(state.reshape(1,inputs_size))
                action = np.argmax(predictionBrute)
            conso += action
            # on exécute l'action choisir et on met à jour le tenseur de données
            datas[index,0] = action * max_power
            datas[index,2] = getR1C1(datas, index)
            nextstate = formatForNetwork(datas, index+1)
            reward = evaluateReward(datas[index,:], mode='C')
            if isinstance(reward, list) == 1:
                self._mem.addSample((state,action,reward[0],nextstate))
            else:
                self._mem.addSample((state,action,reward,nextstate))
            rewardTab.append(reward)
            if train:
                self.trainOnce()
                if args.cloud == 0:
                    barre.update(i)
            npreds = self._steps * goto + i
            self._eps = MIN_EPS + (MAX_EPS - MIN_EPS) * math.exp(-LAMBDA * npreds)

        print("\népisode {} - {} aléatoires / {} réseau".format(self._steps, rpred, apred))
        Text_min, Text_moy, Text_max = getStats(datas[history:-1,1])
        Tint_min, Tint_moy, Tint_max = getStats(datas[history:-1,2])
        print("Text min {:.2f} Text moy {:.2f} Text max {:.2f}".format(Text_min, Text_moy, Text_max))
        print("Tint min {:.2f} Tint moy {:.2f} Tint max {:.2f}".format(Tint_min, Tint_moy, Tint_max))
        if datas.shape[1] > 3:
            #on crée un vecteur w ne contenant que les valeurs de température intérieure en période d'occupation
            w = datas[datas[:,3]!=0,2]
            Tocc_min, Tocc_moy, Tocc_max = getStats(w[history:-1])
            print("Tocc min {:.2f} Tocc moy {:.2f} Tocc max {:.2f}".format(Tocc_min, Tocc_moy, Tocc_max))
        rewardTab = np.array(rewardTab)
        a = np.sum(rewardTab, axis=0)
        print("Récompense(s) {}".format(a))
        self._rewards.append(a)
        self._Text.append([Text_min, Text_moy, Text_max])
        if datas.shape[1] == 3:
            self._Tint.append([Tint_min, Tint_moy, Tint_max])
        if datas.shape[1] > 3:
            self._Tint.append([Tocc_min, Tocc_moy, Tocc_max])
        self._episodes_ts.append(tsvrai)


    def run(self):
        """
        boucle d'exécution
        """
        # Set signal handler to catch SIGINT or SIGTERM and shutdown gracefully
        signal.signal(signal.SIGINT, self._sigint_handler)
        signal.signal(signal.SIGTERM, self._sigint_handler)

        if not self._exit:
            if args.cloud == 0:
                self.play(ts=1606132200)
                self.play(ts=1582620600)

        # Until asked to stop
        while not self._exit:

            if MAX_EPISODES:
                if self._steps > MAX_EPISODES:
                    self._exit = True

            now = time.time()

            if now - self._ts > self._step :
                self._ts += self._step
                if mode == "play":
                    self.play()
                else :
                    self.train()
                self._steps += 1


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
                if graphe:
                    self._rewards=np.array(self._rewards)
                    self._Text = np.array(self._Text)
                    self._Tint = np.array(self._Tint)

                    nb = 211
                    plt.figure(figsize=(20, 10))
                    ax1 = plt.subplot(nb)
                    plt.plot(self._Text[:,0], color="blue")
                    plt.plot(self._Text[:,1], "o", color="blue")
                    plt.plot(self._Text[:,2], color="blue")
                    plt.plot(self._Tint[:,0], color="orange")
                    plt.plot(self._Tint[:,1], "o", color="orange")
                    plt.plot(self._Tint[:,2], color="orange")
                    nb+=1
                    plt.subplot(nb, sharex=ax1)
                    if len(self._rewards.shape) == 2:
                        labels = ["totaux", "confort", "énergie"]
                        for i in range(self._rewards.shape[1]):
                            plt.plot(self._rewards[:,i],label=labels[i])
                        plt.legend()
                    if len(self._rewards.shape) == 1:
                        plt.plot(self._rewards)
                    if args.cloud != 0:
                        plt.savefig("{}".format(name[0:-3]))
                        ax1.set_xlim(0, 200)
                        plt.savefig("{}_begin".format(name[0:-3]))
                        ax1.set_xlim(MAX_EPISODES-200, MAX_EPISODES-1)
                        plt.savefig("{}_end".format(name[0:-3]))
                    else :
                        plt.show()
                        self.play(ts=self._episodes_ts[0])

                if not savedModel :
                    agent.save(name)
                else:
                    i = 1
                    while True:
                        if os.path.isfile("{}_{}".format(i,name)):
                            i+=1
                        else:
                            break
                    agent.save("{}_{}".format(i,name))


if __name__ == "__main__":

    # arguments ligne de commande pour le mode cloud
    import argparse
    # le mode cloud sert à lancer plusieurs entrainement de réseaux successivement
    # en effet, la convergence vers la politique optimale n'est pas garantie et dépend de l'initialisation initiale
    parser = argparse.ArgumentParser(description='Building RL Training Box')

    parser.add_argument("--cloud", action="store", help="1=enforce cloud mode", default=0)
    parser.add_argument("--net-name", action="store", help="network name", type=str)
    parser.add_argument("--tss", action="store", help="starting timestamp", type=int)
    parser.add_argument("--tse", action="store", help="ending timestamp", type=int)
    parser.add_argument("--nb", action="store", help="nombre d'entrainements successifs", type=int, default=1)
    parser.add_argument("--get-feeds", action="store", help="1=rapatrie flux depuis le serveur de terrain", type=int, default=0)

    args = parser.parse_args()

    # tous les fichiers de données nécessaires sont-ils dans le répertoire courant ?
    current_dir = True
    for label in "Text", "Tint", "pompe", "Tdep", "Tret":
        if not os.path.isfile("{}.dat".format(themis[label])):
            current_dir = False
        if not os.path.isfile("{}.meta".format(themis[label])):
            current_dir = False

    if current_dir:
        circuit = themis
        dir ="."

    if args.cloud != 0 :
        mode = "train"
        if args.net_name:
            name = args.net_name
        else:
            name = "RLcontrol.h5"
    else :
        mode = input("train/play ?")
        readline.set_completer_delims('\t')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(simplePathCompleter)
        name = input("nom du réseau ?")
        if not name:
            name = "RLcontrol.h5"
    """
    vérification de la présence d'une extension dans le nom du réseau
    """
    if ".h5" not in name and ".tflite" not in name:
        name = "{}.h5".format(name)

    savedModel = False
    if os.path.isfile(name):
        savedModel = True

    if ".tflite" in name:
        if savedModel and mode=="play":
            lite = True
            import tensorflow.lite as tf
        else:
            print("impossible de continuer - le modèle tensorflow lite doit exister et le mode doit être play")
            exit()
    else:
        lite = False
        import tensorflow as tf

    exit = "Pour continuer, pressez une touche ou CTRL-C pour sortir"
    message = ""

    if savedModel == True and mode == "train":
        message = "Attention, un réseau existe déjà sous ce nom. Il sera chargé et réentrainé."

    if savedModel == False and mode =="play":
        message = "Aucun réseau sous ce nom. On va procéder à une initialisation aléatoire."

    if message != "":
        if args.cloud != 0 :
            print("{} {}".format(message, exit))
        else :
            input("{} {}".format(message,exit))

    if savedModel == True:
        if not lite:
            agent = tf.keras.models.load_model(name)
            test=agent.get_layer(name="states")
            inputs_size = test.get_config()["batch_input_shape"][1]
        else:
            agent = tf.Interpreter(name)
            inputs_size = agent.get_input_details()[0]["shape"][1]
    else :
        agent = initializeNN(inputs_size, name)

    if not lite:
        visNN(agent)

    if args.get_feeds != 0:
        # il faut indiquer les numéros de flux de la machine THEMIS distante
        circuit = themis
        dir = "."
        circuit_download(circuit)

    # on cale les métadonnées sur le flux de température intérieure
    # c'est celui dont l'enregistrement a été déclenché en dernier
    # le flux de température intérieure ne va nous servir
    # qu'à définir la condition initiale sur chaque échantillon
    # on utilisera seulement des Tint synthétiques calculées avec le modèle
    # pour Text, on prendra par contre la vérité terrain

    meta = getMeta(circuit["Tint"],dir)

    # durée du flux en secondes
    fullLength = meta["npoints"] * meta["interval"]
    print("Caractéristiques du flux de température intérieure")
    print("Démarrage : {}".format(meta["start_time"]))
    print("Fin: {}".format(meta["start_time"]+fullLength))
    print("Durée totale en secondes: {}".format(fullLength))

    # _tss est le timestamp à partir duquel le sampling va commencer
    # _tse est le timestamp auquel on arrête le sampling
    # on peut retenir de travailler sur toute la durée du flux
    # ou bien de de se restreindre à un intervalle
    # en effet, celà permet de faire opérer/réentrainer un réseau sur des données qu'il ne connait pas
    if args.cloud != 0 :
        if args.tss :
            _tss=args.tss
        else :
            _tss = meta["start_time"]
        if args.tse :
            _tse=args.tse
        else :
            _tse = meta["start_time"]+fullLength
    else :
        tsMessage = "Saisissez votre timestamp de démarrage"
        tsMessage = "{} ou validez sans rien saisir pour conserver {}\n".format(tsMessage, meta["start_time"])
        _tss=input(tsMessage)
        if not _tss:
            _tss = meta["start_time"]
        else:
            _tss = int(_tss)

        tsMessage = "Saisissez votre timestamp de fin"
        tsMessage = "{} ou validez sans rien saisir pour conserver {}\n".format(tsMessage, meta["start_time"]+fullLength)
        _tse=input(tsMessage)
        if not _tse:
            _tse = meta["start_time"]+fullLength
        else:
            _tse = int(_tse)

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
    if args.cloud == 0:
        input("pressez une touche pour continuer")

    Text = PyFina(circuit["Text"], dir, _tss, interval, npoints)
    Tint = PyFina(circuit["Tint"], dir, _tss, interval, npoints)

    # on utilisera le flux de fonctionnement de la pompe
    # pour produire un historique de chauffage "réaliste"
    pompe = PyFina(circuit["pompe"], dir, _tss, interval, npoints)
    Tdep = PyFina(circuit["Tdep"], dir, _tss, interval, npoints)
    Tret = PyFina(circuit["Tret"], dir, _tss, interval, npoints)
    # QcTrue est uniquement informatif, il n'est pas utilisé en pratique
    QcTrue = (Tdep - Tret) * pompe * Cw * circuit["flow_rate"]
    # on ne garde que les valeurs de deltaT positives !!
    QcTrue = np.maximum(np.zeros(QcTrue.shape[0]),QcTrue)
    # on construit un flux simplifié
    Qc = pompe * max_power

    agenda = basicAgenda(npoints,interval, _tss,-1,-1,schedule=schedule)

    # affichage de toutes les données chargées
    if args.cloud == 0:
        plt.figure(figsize=(20, 10))
        ax1=plt.subplot(211)
        plt.plot(Text.timescale(),Text)
        plt.plot(Tint.timescale(),Tint)
        ax2=ax1.twinx()
        plt.plot(pompe.timescale(),Qc, color="yellow")
        plt.plot(pompe.timescale(),QcTrue, color="red")
        ax3 = plt.subplot(212,  sharex=ax1)
        plt.plot(Text.timescale(),agenda)
        plt.show()

    if args.cloud == 0 or args.nb == 1:
        sandbox = Training(5)
        sandbox.run()
        sandbox.close()
        plt.close()
    else :
        suffix = name
        for i in range(args.nb):
            name = "{}_{}".format(i,suffix)
            if i > 0:
                agent = initializeNN(inputs_size, name)
                visNN(agent)
            sandbox = Training(5)
            sandbox.run()
            sandbox.close()
            plt.close()
