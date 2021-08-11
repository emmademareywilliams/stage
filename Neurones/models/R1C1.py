import numpy as np
from math import exp

def R1C1(step, R, C, Qc, Text, Tint):
    """
    calcule le point suivant avec la méthode des trapèzes
    """
    x = Tint * exp(-step/(R*C)) + step * 0.5 * (1 + exp(-step/(R*C))) * ( Qc / C + Text / (R*C) )

    return x

def R1C1variant(step, R, C, Qc, Text, Tint):
    """
    calcule le point suivant avec la méthode des trapèzes - variante
    Text et Qc sont des vecteurs de taille 2 contenant les valeurs à t et t+step
    """
    delta = exp(-step/(R*C)) * ( Qc[0] / C + Text[0] / (R*C) ) + Qc[1] / C + Text[1] / (R*C)
    x = Tint * exp(-step/(R*C)) + step * 0.5 * delta

    return x

def R1C1SBSsim(step, R, C, Qc, Text, T0):
    """
    simulation utilisant le simple calcul du point suivant
    """
    n = Text.shape[0]
    x = np.zeros(n)
    xx = np.zeros(n)
    x[0] = T0
    xx[0] = T0
    for i in range(1,n):
        x[i] = R1C1variant(step, R, C, Qc[i-1:i+1], Text[i-1:i+1], x[i-1])
        xx[i] = R1C1(step, R, C, Qc[i], Text[i], x[i-1])

    return x, xx


def R1C1sim(step, R, C, Qc, Text, T0):
    """
    calcul des intégrales par produit de convolution
    """
    n = Text.shape[0]
    xr = np.arange(0,n*step,step)
    a = np.zeros(n)
    for i in range(n):
        a[i] = exp(-xr[i]/(R*C))

    b = Qc/C + Text/(R*C)

    x = T0 * a + step * np.convolve(a,b)[0:n]

    return x

def R1C1fonc(step, R, C, Qc, Text, truth, verbose=True):
    x = R1C1sim(step, R, C, Qc, Text, truth[0])
    result = 0.5*np.sum(np.square(x-truth)) / x.shape[0]
    if verbose:
        print("p is {} {} func is {}".format(R,C,result))
    return result

def R1C1grad(step, R, C, Qc, Text, truth, verbose=True):
    n = Text.shape[0]
    xr = np.arange(0,n*step,step)
    a = np.zeros(n)
    c = np.zeros(n)
    for i in range(n):
        c[i] = exp(-xr[i]/(R*C))
        a[i] = xr[i]*c[i]/(R**2 * C)
    b = Qc/C + Text/(R*C)
    d = Text/(R**2 * C)
    gradR = a*truth[0] + step * np.convolve(a,b)[0:n] - step * np.convolve(c,d)[0:n]
    gradC = a*truth[0]*R/C + step * np.convolve(a*R/C,b)[0:n] - step * np.convolve(c,b/C)[0:n]

    x = R1C1sim(step, R, C, Qc, Text, truth[0])
    fr = np.sum(gradR * (x - truth)) / x.shape[0]
    fc = np.sum(gradC * (x - truth)) / x.shape[0]
    result = np.array([fr, fc])
    if verbose:
        print("p is {} {} gradient is {}".format(R,C,result))
    return result

class R1C1Zone:
    """
    le modèle RC le plus simple
    """
    def __init__(self,step,p):
        self._step = step
        self._C = p[0]
        self._R = p[1]

    def predict(self, Qc, Text, T0):
        """
        Qc : vecteur numpy des puissances de chauffage en W

        Text : vecteur numpy des températures des chauffage

        T0 : valeur de la condition initiale pour la température intérieure
        """
        Tint = R1C1sim(self._step, self._R, self._C, Qc, Text, T0)
        return Tint
