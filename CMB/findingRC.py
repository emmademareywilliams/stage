import numpy as np
from math import exp
import matplotlib.pylab as plt
import datetime
import time

from PyFina import PyFina

flow_rate = 50 #m3/h  ==> première approximation
Cw = 1162.5 #Wh/m3/K


def HumanTimetoUnix(datetime):
    """
    inverse function of secondToHumanTime, aka gives the Unix time stamp associated with a given dates

    datetime: datetime object corresponding to a date (yyyy - mm - dd)
    returns a Unix number (int)
    """
    return int(time.mktime(datetime.timetuple()))


message_month = "Please choose the month (number of the month) \n"
month = input(message_month)
message_day = "then the number of the day :\n"
day = input(message_day)

date = datetime.datetime.strptime('2021 {} {} 04:00'.format(month, day), '%Y %m %d %H:%M')
start = HumanTimetoUnix(date)

dir = "/var/opt/emoncms/phpfina"  # attention erreur bête : aller chercher les données modifiées sur emoncms !
#start = 1613876400
step = 3600

window = 30  # number of days
nb = window*24*3600//step

Text = PyFina(9, dir, start, step, nb)
Tint = PyFina(29, dir, start, step, nb)
heating = PyFina(28, dir, start, step, nb)

# print(Text)
# on sait que la valeur minimale dans l'autopilot représente l'arrêt du système de chauffage
# c'est ainsi sur presque tous les systèmes --> pour savoir quand on chauffe

deltatemp = 10  # approximation
Qc = flow_rate * Cw * deltatemp * heating

from scipy import signal

def sim(step, R, C, Qc, Text, T0, check=False):
    n = Text.shape[0]
    xr = np.arange(0,n*step,step)
    a = np.zeros(n)
    for i in range(n):
        a[i] = exp(-xr[i]/(R*C))

    b = Qc/C + Text/(R*C)

    x = T0 * a + step * np.convolve(a,b)[0:n]

    if check:
        print("n is {} and x is {}".format(n,x.shape))
        print(x)
        ax1=plt.subplot(111)
        plt.plot(np.convolve(a,b))
        #plt.plot(signal.fftconvolve(a,b))
        ax2=ax1.twinx()
        plt.plot(x)
        plt.show()

    return x

def fonc(step, R, C, Qc, Text, truth, verbose=True):
    x = sim(step, R, C, Qc, Text, truth[0])
    result = 0.5*np.sum(np.square(x-truth)) / x.shape[0]
    if verbose:
        print("p is {} {} func is {}".format(R,C,result))
    return result

def grad(step, R, C, Qc, Text, truth, verbose=True):
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

    x = sim(step, R, C, Qc, Text, truth[0])
    fr = np.sum(gradR * (x - truth)) / x.shape[0]
    fc = np.sum(gradC * (x - truth)) / x.shape[0]
    result = np.array([fr, fc])
    if verbose:
        print("p is {} {} gradient is {}".format(R,C,result))
    return result

wanatest = False
if wanatest == True:
    R = 1.6e-4
    C = 2.25e8
    T = sim(step, R, C, Qc, Text, Tint[0], check=True)
    input("press a key or abort")

p0=np.array([1e-5,1e8])
# weights
w0=np.array([2.0,7.0])

def f(w):
    p=p0*w
    return fonc(step, p[0], p[1], Qc, Text, Tint)

def g(w):
    p=p0*w
    return p0*grad(step, p[0], p[1], Qc, Text, Tint)

from scipy import optimize
res=optimize.minimize(f, w0, method="BFGS", jac=g, options={"disp":True})
print(res)
popt=res["x"]*p0
print(popt)

"""
Plotting the results:
"""

localstart = datetime.datetime.fromtimestamp(start)
utcstart = datetime.datetime.utcfromtimestamp(start)
title = "Results for the North circuit \n Begins on the :\nUTC {}\n{} {}".format(utcstart, time.tzname[0], localstart)

xr = np.arange(0,nb*step,step)
xr_hour = xr/step
Tint_sim = sim(step, popt[0], popt[1], Qc, Text, Tint[0])

plt.subplot(211)
plt.plot(xr_hour,Text, label="Text")
plt.plot(xr_hour,Tint, label="True Tint")
plt.plot(xr_hour,Tint_sim[0:xr.shape[0]], label="Tint sim")
plt.title(title)
plt.ylabel('temperature (°C)')
plt.legend()

plt.subplot(212)
plt.plot(xr_hour, heating)
plt.xlabel('time (time step = {} s)'.format(step))
plt.ylabel('pump operation')
plt.show()
