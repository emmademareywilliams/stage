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
MAX_EPISODES = 500

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

dir = "/var/opt/emoncms/phpfina"

# sampling interval in seconds
interval = 3600
#interval = 900
schedule = np.array([ [7,17], [7,17], [7,17], [7,17], [7,17], [-1,-1], [-1,-1] ])

# le circuit
# flow_rate en m3/h
# numéro de flux sur le serveur local synchronisé avec le serveur de terrain via le module sync
circuit = {"name":"Nord", "Text":9, "Tint":29, "flow_rate":5, "pompe":28, "Tdep":10, "Tret":11}

Cw = 1162.5 #Wh/m3/K
max_power = circuit["flow_rate"] * Cw * 15
# la loi d'eau du circuit
coeffs = np.array([[-10,20],
                   [85 ,40]])

# température de consigne en °C
# confort temperature set point
Tc = 20

# le modèle qui va décrire l'évolution de la température intérieure
# un modèle électrique équivalent de type R1C1
R = 3.08814171e-04
C = 8.63446560e+08

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
numPar = 3
# nombre d'actions possibles  : 2 = on chauffe ou pas
# pour l'instant, on reste simple
numAct = 2

# nombre d'intervalles sur lequel la simulation sera menée
# 60 correspond à un weekend
goto = 60*3600//interval
#goto = 8*24*3600//interval

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



def initializeNN(inputs_size, name, init_mode=-1):
    """
    initialisation du réseau neurone qui jouera le rôle de contrôleur ou agent énergétique

    son rôle est de produire l'action énergétique (chauffage On ou Off)

    La détermination de Tint après application de cette action est faite :

    - soit par le modèle par calcul
    - soit par l'environnement réel par monitoring
    """
    tf.keras.backend.set_floatx('float64')
    if init_mode == 1 :
        initializer = tf.keras.initializers.Ones()
    if init_mode == 0 :
        initializer = tf.keras.initializers.Zeros()
    inputs = tf.keras.Input(shape=(inputs_size, ), name='states')
    if init_mode == -1 :
        x = tf.keras.layers.Dense((50), activation='relu')(inputs)
    else :
        x = tf.keras.layers.Dense((50), kernel_initializer=initializer, activation='relu')(inputs)
    # pour ajouter de la profondeur (pas utilisé pour l'instant)
    #x = tf.keras.layers.Dense((50), activation='relu')(x)
    outputs = tf.keras.layers.Dense(numAct,activation='linear')(x)
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
    print(agent.get_weights())

def setStart(ts=None, wsize = wsize):
    """
    tire un timestamp aléatoirement avant fin mai OU après début octobre

    ou le fixe à une valeur donnée pour rejouer un épisode (ex : 1588701000)

    retourne la position dans la timeserie et le timestamp correspondant
    """
    if ts is None:
        start = _tss
        if numPar != 6:
            end = _tse - wsize * interval
        else:
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

def getStats(datas):
    """
    stats ultra basiques (min, max, moyenne) sur vecteur datas
    """
    min = np.amin(datas)
    max = np.amax(datas)
    moy = np.mean(datas)
    return min,moy,max

def waterLaw(coeffs, i=0):
    """
    loi d'eau (peu utilisée dans le simulateur jusqu'à présent)

    coeffs : tableau numpy de taille (2,n) - 2 lignes et n colonnes

    coeffs[0,:] : série de températures extérieures

    coeffs[1,:] : série des températures de départ correspondantes

    ```
    coeffs = np.array([[-10, 20],
                       [85 , 40]])
    ```

    ou encore :
    ```
    coeffs = np.array([[-20, -10, 20 , 30],
                       [95 , 85 , 40 , 30]])
    ```

    """
    a = (coeffs[1,i+1]-coeffs[1,i])/(coeffs[0,i+1]-coeffs[0,i])
    b = coeffs[1,i] - a * coeffs[0,i]
    return a, b


"""
Stratégie industrielle :
"""

def industryPlayReductions(datas, index, max_power=max_power, coeffs = None):
    """
    simulation d'un pilotage par agenda avec réduit de nuit/week-end et préchauffage

    stratégie courante qt les capteurs de temp. intérieure n'ont pas de rôle dans la régul. de la distribution

    le contrôle en température intérieure est svt réalisé au niveau des émetteurs par robinets thermostatiques
    """
    if coeffs is not None:
        a_cells, b_cells = waterLaw(coeffs)
        Tdep = a_cells * datas[:,1] + b_cells
        Tret = 4 + 0.8 * Tdep
        power = circuit["flow_rate"] * Cw * (Tdep - Tret)
    else :
        power = np.ones(datas.shape[0]) * max_power
    for i in range(index,datas.shape[0]):
        action = datas[i,3]
        # pas d'occupation
        if datas[i,3] == 0:
            # il fait doux dehors, on peut faire des économies
            if datas[i,1] >= 10 and datas[i,1] < Tc+2:
                action = 0.1
            # il fait froid, hors-gel à minima
            if datas[i,1] < 10:
                action = 0.4
            # le préchauffage
            if datas[i,4] <= 3:
                action = 1
        # s'il fait chaud dehors, qu'on soit occupé ou non, pas la peine de chauffer
        if datas[i,1] >= Tc+2:
            action = 0
        datas[i,0] = action * power[i]
        datas[i,2] = getR1C1(datas, i)
    heating=True
    # on vérifie si on a chauffé ou pas
    if not np.any(datas[index:,0]):
        heating=False
    return {"heating":heating, "datas":datas}

def industryPlayHystNRed(datas, index, max_power=max_power, coeffs = None):
    """
    simulation d'un pilotage par agenda avec :

    - réduit de nuit/week-end
    - préchauffage
    - contrôle hysteresys sur température intérieure en occupation
    """
    if coeffs is not None:
        a_cells, b_cells = waterLaw(coeffs)
        Tdep = a_cells * datas[:,1] + b_cells
        Tret = 4 + 0.8 * Tdep
        power = circuit["flow_rate"] * Cw * (Tdep - Tret)
    else :
        power = np.ones(datas.shape[0]) * max_power
    for i in range(index,datas.shape[0]):
        # l'ation de chauffage suit l'occupation
        # pas d'occupation > pas de chauffage > action = 0
        # occupation > on chauffe > action = 1
        action = datas[i,3]
        # partant de ce choix basique, on raffine en traitant des cas particuliers
        # hors occupation, on prévoit un hors-gel et un préchauffage
        if datas[i,3] == 0:
            # hors-gel déclenché si température extérieure inférieure à 10
            if datas[i,1] < 10:
                action = 0.4
            # préchauffage si on est proche de l'arrivée du personnel
            if datas[i,4] <= 3:
                action = 1
        # en occupation, si on est dans la zone de confort > hysteresys
        else :
            if datas[i-1,2] > Tc + 1 or datas[i-1,2] < Tc -1:
                action = datas[i-1,2] <= Tc
        datas[i,0] = action * power[i]
        datas[i,2] = getR1C1(datas, i)
    heating=True
    # on vérifie si on a chauffé ou pas
    if not np.any(datas[index:,0]):
        heating=False
    return {"heating":heating, "datas":datas}

def industryPlayHysteresis(datas, index, max_power=max_power, coeffs = None):
    if coeffs is not None:
        a_cells, b_cells = waterLaw(coeffs)
        Tdep = a_cells * datas[:,1] + b_cells
        Tret = 4 + 0.8 * Tdep
        power = circuit["flow_rate"] * Cw * (Tdep - Tret)
    else :
        power = np.ones(datas.shape[0]) * max_power
    for i in range(index,datas.shape[0]):
        action = datas[i,3]
        if datas[i-1,2] > Tc + 1 or datas[i-1,2] < Tc -1:
            action = datas[i-1,2] <= Tc
        datas[i,0] = action * power[i]
        datas[i,2] = getR1C1(datas, i)
    heating=True
    # on vérifie si on a chauffé ou pas
    if not np.any(datas[index:,0]):
        heating=False
    return {"heating":heating, "datas":datas}


'''
Modèle IA :
'''

def modelPlayWeekInHysteresys(datas, index, Tc, max_power, pos):
    """
    le modèle joue un épisode de la vraie vie intégrant des périodes d'occupation et de non-occupation

    **il cumule les rôles de contrôleur et d'environnement !**
    """
    for i in range(index,datas.shape[0]):
        if datas[i,3] == 0:
            # aucune occupation
            # prédiction à la cible en chauffant
            tof = int(datas[i,4])
            _Qc = np.ones(tof) * max_power
            Tint_sim = R1C1sim(interval, R, C, _Qc, Text[pos+i:pos+i+tof], datas[i-1,2])
            if Tint_sim[-1] <= Tc:
                datas[i,0]= max_power
        else:
            # occupation
            if datas[i-1,2] > Tc+hh or datas[i-1,2] < Tc-hh :
                action = datas[i-1,2] <= Tc
                datas[i,0] = action * max_power
            else:
                # on est dans la fenêtre > on ne change rien :-)
                datas[i,0] = datas[i-1,0]
        datas[i,2] = getR1C1(datas, i)

    heating=True
    # on vérifie si on a chauffé ou pas
    if not np.any(datas[index:,0]):
        heating=False

    return {"heating":heating, "datas":datas}

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

def modelPlayNonOccupation(datas, index, Tc, max_power):
    """
    le modèle joue une période de non occupation (week-end)

    **il cumule les rôles de contrôleur et d'environnement !**

    On veut garantir une température intérieure Tc à la fin

    retourne un hash composé de :

    - un booléen indiquant s'il faut chauffer ou non
    - un booléen indiquant si la température de consigne est atteinte
    - l'indice à partir duquel il faut chauffer (-1 si le chauffage n'est pas nécessaire)
    - un tenseur de données contenant les données sources, le scénario de chauffage et la température intérieure simulée

    """
    # on regarde ce qu'il se passe sans chauffage
    datas[index:,2] = R1C1sim(interval, R, C, datas[index:,0], datas[index:,1], datas[index-1,2])
    # s'il n'est pas nécessaire de chauffer, on peut s'arrêter là :-)
    heating = False
    success = True
    i = -1
    # sinon....
    if datas[-1,2] < Tc:
        heating = True
        success=False
        i=index
        while i < datas.shape[0]:
            _Qc = np.ones(datas.shape[0]-i) * max_power
            Tint_sim = R1C1sim(interval, R, C, _Qc, datas[i:,1], datas[i,2])
            if Tint_sim[-1] < Tc:
                # il faut chauffer
                break
            else:
                # il n'est pas encore temps de déclencher le chauffage
                i+=1
        if i == datas.shape[0]: i-=1
        datas[i:,2] = Tint_sim
        datas[i:,0] = _Qc
        if verbose:
            info = "on chauffe à l'indice {}".format(i)
            info = "{} - {:.2f}°C à la cible".format(info,Tint_sim[-1])
            print(info)
        # contrôle hysteresys à la cible pour voir si consigne est atteinte
        if Tint_sim[-1]<=Tc+1 and Tint_sim[-1]>=Tc-1:
            success=True

    return {"heating":heating, "success":success, "index":i, "datas":datas}

"""
FONCTIONS RECOMPENSE/REWARD

En donnant à la fonction,
- les 3 premiers éléments : on cherche à ce que le controleur maintienne en permanence la température de consigne
- les 6 éléments : on cherche à ce que le contrôleur gère des périodes de non-occupation

-> TO DO : il faudrait aussi qu'il soit apte à prendre en compte une température de consigne variable.....
"""
def CP(dline):
    """
    penalité de confort utilisée pour entrainer le réseau à recréer en permanence un comportement de type hystéresys

    dans toutes les fonctions CP*, dline est composé au maximum des éléments suivants :

    - 0) la puissance de chauffage
    - 1) la température extérieure à i
    - 2) la température intérieure à i
    - 3) occupation 0/1 à i,
    - 4) nombre d'intervalles entre i et le changement d'occupation (time of flight - tof)
    - 5) la température de consigne * occupation à i

    dline : vecteur des données [Qc, Text, Tint, Occ, Tof, Tc] au point/instant i

    dline = une ligne du tenseur datas
    """
    confortPenalty = abs(dline[2] - Tc)
    return confortPenalty

def CPA(dline):
    """
    penalité de confort utilisée pour entrainer le réseau à subir en alternance des périodes d'occupation et d'inoccupation

    lors des périodes d'occupation, le réseau se comporte comme un hystéresys

    mode A
    """
    # le bâtiment n'est pas occupé
    if dline[3] == 0:
        confortPenalty = abs(dline[2] - Tc) / (dline[4] + 1)
    # le bâtiment est occupé
    else:
        confortPenalty = abs(dline[2] - Tc)
    return confortPenalty

def CPB(dline):
    """
    penalité de confort utilisée pour entrainer le réseau à subir en alternance des périodes d'occupation et d'inoccupation

    mode B - probablement trop orienté
    """
    confortPenalty = 0
    # calcule une pénalité si on est dans un des 2 cas suivants :
    # 1) on chauffe
    # 2) la température intérieure est inférieure à la consigne
    # en effet, il semble intuitif de ne pas pénaliser le réseau
    # s'il a décidé de ne pas chauffer
    # ET si la température intérieure résultant de cette action est au dessus de la consigne
    if dline[0] !=0 or dline[2] < Tc:
        # le bâtiment n'est pas occupé
        if dline[3] == 0:
            confortPenalty = abs(dline[2] - Tc) / (dline[4] + 1)
        # le bâtiment est occupé
        else:
            confortPenalty = abs(dline[2] - dline[5])
    return confortPenalty

def CPC(dline):
    """
    penalité de confort utilisée pour entrainer le réseau à subir en alternance des périodes d'occupation et d'inoccupation

    mode C
    """
    # le bâtiment n'est pas occupé ET sa température est en dessous de la consigne
    if dline[3] == 0 and dline[2] <= Tc + hh :
        confortPenalty = abs(dline[2] - Tc) / (dline[4] + 1)
    # le bâtiment est occupé OU sa température est au dessus de la consigne
    else:
        confortPenalty = abs(dline[2] - Tc)
    return confortPenalty

def evaluateReward(dline, mode='A', conso=-1):
    """
    calcule une récompense de type confort et/ou énergie

    HH : hystérésis simple sans tenir compte de l'occupation
    """
    if mode == 'HH':
        confortPenalty = CP(dline)
    if mode == 'A':
        confortPenalty = CPA(dline)
    if mode == 'B':
        confortPenalty = CPB(dline)
    if mode == 'C':
        confortPenalty = CPC(dline)

    if conso != -1:
        energyPenalty = conso / goto
        reward = - confortPenalty - energyPenalty
        return [reward, -confortPenalty, -energyPenalty]
    else :
        reward = - confortPenalty
        return reward

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
            #result = modelPlayHysteresys(copy.deepcopy(datas), history, Tc, max_power)
            #result = modelPlayNonOccupation(copy.deepcopy(datas), history, Tc, max_power)
            result = modelPlayWeekInHysteresys(copy.deepcopy(datas), history, Tc, max_power,pos)

            labelModel = "modèle"
        else:
            #result = industryPlayReductions(copy.deepcopy(datas), history)
            #result = industryPlayHystNRed(copy.deepcopy(datas), history)
            result = industryPlayHysteresis(copy.deepcopy(datas), history)
            labelModel = "réduits nuit/week-end"
        mConso = int(np.sum(result["datas"][history:,0]) / 1000)
        """
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
        """
        title = "épisode {} - {} {}".format(self._steps,tsvrai, tsToHuman(tsvrai))
        title = "{}\n".format(title)
        if result["heating"]:
            title = "{}\n conso {} {}".format(title, labelModel, mConso)
            if "index" in result:
                title = "{} indice {}".format(title,result["index"])
            if "success" in result and not result["success"]:
                title = "{}\n consigne non atteinte : besoin de plus de puissance ".format(title)
        else:
            title = "{}\n modèle - chauffage pas nécessaire".format(title)

        # matérialisation de la zone de confort par un hystéréris de 2 degrés autour de la température de consigne
        zoneconfort = Rectangle((xr[0], Tc-hh), xr[-1]-xr[0], 2*hh, facecolor='g', alpha=0.5, edgecolor='None', label="zone de confort")
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

        ax1 = plt.subplot(211)
        plt.title(title)
        plt.ylabel("Temp. extérieure °C")
        plt.plot(xr, datas[:-1,1], color="blue", label="Text")
        if datas.shape[1] >= 5:
            for v in zonesOccText:
                ax1.add_patch(v)
        plt.legend(loc='upper left')
        ax2 = ax1.twinx()
        ax2.add_patch(zoneconfort)
        plt.ylabel("Temp. intérieure °C")
        plt.plot(xr, result["datas"][:-1,2], color="orange", label="Tint {}".format(labelModel))
        plt.legend(loc='upper right')
        plt.subplot(212, sharex=ax1)
        plt.ylabel("Consommation W")
        plt.plot(xr, result["datas"][:-1,0], color="orange", label=labelModel)
        plt.legend()
        plt.show()

        """
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
        """

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
            reward = evaluateReward(datas[index,:], mode='HH')
            if isinstance(reward, list) == 1:
                self._mem.addSample((state,action,reward[0],nextstate))
            else:
                self._mem.addSample((state,action,reward,nextstate))
            rewardTab.append(reward)
            if train:
                self.trainOnce()
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
            pass

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

    exit = "Pour continuer, pressez une touche ou CTRL-C pour sortir"
    message = ""

    if savedModel == True and mode == "train":
        message = "Attention, un réseau existe déjà sous ce nom. Il sera chargé et réentrainé."

    if savedModel == False and mode =="play":
        message = "Aucun réseau sous ce nom. On va procéder à une initialisation aléatoire."

    if message != "":
        input("{} {}".format(message,exit))

    if savedModel == True:
        agent = tf.keras.models.load_model(name)
        test=agent.get_layer(name="states")
        inputs_size = test.get_config()["batch_input_shape"][1]
    else :
        agent = initializeNN(inputs_size, name)

    visNN(agent)


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
    input("pressez une touche pour continuer")

    Text = PyFina(circuit["Text"], dir, _tss, interval, npoints)
    Tint = PyFina(circuit["Tint"], dir, _tss, interval, npoints)

    # on utilisera le flux de fonctionnement de la pompe
    # pour produire un historique de chauffage "réaliste"
    pompe = PyFina(circuit["pompe"], dir, _tss, interval, npoints)
    # on construit un flux simplifié
    Qc = pompe * max_power

    agenda = basicAgenda(npoints,interval, _tss,-1,-1,schedule=schedule)

    # affichage de toutes les données chargées
    plt.figure(figsize=(20, 10))
    ax1=plt.subplot(211)
    plt.plot(Text.timescale(),Text, label='Text')
    plt.plot(Tint.timescale(),Tint, label='Tint')
    ax2=ax1.twinx()
    plt.plot(pompe.timescale(),Qc, color="yellow", label='heating')
    plt.legend()
    ax3 = plt.subplot(212,  sharex=ax1)
    plt.plot(Text.timescale(),agenda, label='occupation')
    plt.legend()
    plt.show()

    sandbox = Training(5)
    sandbox.run()
    sandbox.close()
    plt.close()
