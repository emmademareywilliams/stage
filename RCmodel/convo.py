
import numpy as np
from math import exp
import matplotlib.pylab as plt
import datetime
import time

from PyFina import PyFina, getMeta


Cw = 1162.5  #Wh/m3/K

dir = "phpfina_cerema2020"
#start = 1603992600

message_circuit = "please select the circuit to be studied : \n 1 --> cell circuit  \n 2 --> North circuit \n " \
                  "3 --> South circuit \n"
i = input(message_circuit)

#i = 1

nb_circuit = float(i)
if nb_circuit == 1:  # circuit cellules
    nb_Text = 18
    nb_Tint = 56
    nb_Tdepart = 25
    nb_Tretour = 29
    nb_autop = 57
    nb_pompe = 26
    flow_rate = 5.19

elif nb_circuit == 2:  # circuit Nord
    nb_Text = 18
    nb_Tint = 48
    nb_Tdepart = 31
    nb_Tretour = 35
    nb_autop = 58
    nb_pompe = 32
    flow_rate = 6.5

elif nb_circuit == 3:  # circuit Sud
    nb_Text = 18
    nb_Tint = 51
    nb_Tdepart = 36
    nb_Tretour = 40
    nb_autop = 59
    nb_pompe = 37
    flow_rate = 4.2

else:
    print("This circuit does not exist. ")

"""
on commence la simulation au start time maximal de toutes nos donnees : 
"""

start_array = [getMeta(nb_Text, dir)["start_time"], getMeta(nb_Tint, dir)["start_time"],
               getMeta(nb_Tdepart, dir)["start_time"], getMeta(nb_Tretour, dir)["start_time"],
               getMeta(nb_autop, dir)["start_time"], getMeta(nb_pompe, dir)["start_time"]]
start = max(start_array)

meta_Text = getMeta(nb_Text, dir)
length = meta_Text["npoints"] * meta_Text["interval"]


def secondToMonth(mois):
    """
    :param mois: string qui prend les 3 premieres lettres du mois
    :return: nombre de secondes depuis le 1er janvier et jusqu'au 1er du mois (int)
    """
    y = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    num_m = y.index(mois)
    sec = 3600*24*30*num_m  #approx : 30 jours dans un mois
    return sec


def secondToDay(nb_jour):
    """
    :param nb_jour: entier qui correspond au numero du jour
    :return: nombre de secondes depuis le 1er du mois et jusqu'au numero du jour (int)
    """
    sec = 3600*24*nb_jour
    return sec


message_mois = "Please choose the month (first three letters, e.g. january --> jan) \n"
mois = input(message_mois)
message_jour = "then the number of the day :\n"
jour = input(message_jour)

""" 
on choisit la date a laquelle on veut commencer la simulation :
"""

start = start + secondToMonth(mois) + secondToDay(int(jour)-1)
step = 3600
nb = 10*24*3600//step

Text = PyFina(nb_Text, dir, start, step, nb)
Tint = PyFina(nb_Tint, dir, start, step, nb)

Tdepart = PyFina(nb_Tdepart, dir, start, step, nb)
Tretour = PyFina(nb_Tretour, dir, start, step, nb)

autopilot = PyFina(nb_autop, dir, start, step, nb)
pompe = PyFina(nb_pompe, dir, start, step, nb)

# on sait que la valeur minimale dans l'autopilot represente l'arret du systeme de chauffage
# c'est ainsi sur presque tous les systemes --> pour savoir quand on chauffe

lower = np.min(autopilot)
tmp = lower * np.ones(nb)
heating = (autopilot - tmp)
upper = np.max(heating)
heating = heating / upper

Tdepart = Tdepart * heating
Tretour = Tretour * heating
#Qc = flow_rate * Cw * (Tdepart - Tretour)
""" 
loi de l'eau : on remarque que le delta de temperature est toujours plus ou moins de 15 
"""
Qc = flow_rate * Cw * 15 * heating

from scipy import signal


def sim(step, R, C, Qc, Text, T0, check=False):
    n = Text.shape[0]
    xr = np.arange(0, n*step, step)
    a = np.zeros(n)
    for i in range(n):
        a[i] = exp(-xr[i]/(R*C))

    b = Qc/C + Text/(R*C)

    x = T0 * a + step * np.convolve(a, b)[0:n]

    if check:
        print("n is {} and x is {}".format(n, x.shape))
        print(x)
        ax1 = plt.subplot(111)
        plt.plot(np.convolve(a, b))
        #plt.plot(signal.fftconvolve(a,b))
        ax2=ax1.twinx()
        plt.plot(x)
        plt.show()

    return x


def fonc(step, R, C, Qc, Text, truth, verbose=True):
    x = sim(step, R, C, Qc, Text, truth[0])
    result = 0.5*np.sum(np.square(x-truth)) / x.shape[0]
    if verbose:
        print("p is {} {} func is {}".format(R, C, result))
    return result


def grad(step, R, C, Qc, Text, truth, verbose=True):
    n = Text.shape[0]
    xr = np.arange(0, n*step, step)
    a = np.zeros(n)
    c = np.zeros(n)
    for i in range(n):
        c[i] = exp(-xr[i]/(R*C))
        a[i] = xr[i]*c[i]/(R**2 * C)
    b = Qc/C + Text/(R*C)
    d = Text/(R**2 * C)
    gradR = a*truth[0] + step * np.convolve(a, b)[0:n] - step * np.convolve(c, d)[0:n]
    gradC = a*truth[0]*R/C + step * np.convolve(a*R/C, b)[0:n] - step * np.convolve(c, b/C)[0:n]

    x = sim(step, R, C, Qc, Text, truth[0])
    fr = np.sum(gradR * (x - truth)) / x.shape[0]
    fc = np.sum(gradC * (x - truth)) / x.shape[0]
    result = np.array([fr, fc])
    if verbose:
        print("p is {} {} gradient is {}".format(R, C, result))
    return result

wanatest = False
if wanatest == True:
    """
    valeurs initiales de R et de C
    """
    R = 1.6e-4
    C = 2.25e8
    T = sim(step, R, C, Qc, Text, Tint[0], check=True)
    input("press a key or abort")

p0 = np.array([1e-5, 1e7])
# weights
w0 = np.array([2.0, 7.0])


def f(w):
    p = p0*w
    return fonc(step, p[0], p[1], Qc, Text, Tint)


def g(w):
    p=p0*w
    return p0*grad(step, p[0], p[1], Qc, Text, Tint)


from scipy import optimize
res = optimize.minimize(f, w0, method="BFGS", jac=g, options={"disp":True})
print(res)
popt = res["x"]*p0
print(popt)

xr_sec = np.arange(0, nb*step, step)
xr_hour = xr_sec/3600
Tint_sim = sim(step, popt[0], popt[1], Qc, Text, Tint[0])

localstart = datetime.datetime.fromtimestamp(start)
utcstart = datetime.datetime.utcfromtimestamp(start)

if nb_circuit == 1:
    location = 'cell'
elif nb_circuit == 2:
    location = 'North'
elif nb_circuit == 3:
    location = 'South'

title = "Results for the {} circuit \n Begins on the :\nUTC {}\n{} {}".format(location, utcstart, time.tzname[0], localstart)

# Trace des differentes temperatures
plt.subplot(211)
plt.plot(xr_hour, Text, label="Text")
plt.plot(xr_hour, Tint, label="True Tint")
plt.plot(xr_hour, Tint_sim[0:xr_hour.shape[0]], label="Tint sim")
plt.title(title)
plt.xlabel('time (time step = {} s)'.format(step))
plt.ylabel('temperature')
plt.legend()

# Trace du fonctionnement de l'autopilote / pompe
autop_norm = [(k-min(autopilot))/(max(autopilot)-min(autopilot)) for k in autopilot]
plt.subplot(212)
plt.plot(xr_hour, pompe, label='pump')
plt.plot(xr_hour, autop_norm, '--', label='autopilot')
plt.xlabel('time (time step = {} s)'.format(step))
plt.legend(loc='upper right')

# Trace de la temperature de retour en fonction de la temperature de depart
#       --> a tracer seulement quand la pompe fonctionne !
#plt.subplot(313)
#plt.plot(Tdepart, Tretour, 'o')
#plt.xlabel('temperature de depart')
#plt.ylabel('temperature de retour')

plt.show()
plt.close()

"""
Je voudrais qu'il me le mette sur GitHub svp...
"""
