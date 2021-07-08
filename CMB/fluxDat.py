import time
import math
import struct
import numpy as np
import os.path

# if want to work on the active directory, just use dir="."
dir="./Data/phpfina"


def getMetas(nb,dir=dir):
    """
    read meta given a feed number
    print (interval,starting timestamp)
    """
    f=open("{}/{}.meta".format(dir,nb),"rb")
    f.seek(8,0)
    hexa = f.read(8)
    aa= bytearray(hexa)
    if len(aa)==8:
      decoded=struct.unpack('<2I', aa)
    print(decoded)
    f.close()
    return decoded


def createFeed(nb,data,dir=dir):
    """
    create a dat file given :
    - a feed number
    - a numpy vector of data
    """
    f=open("{}/{}.dat".format(dir,nb),"wb")
    format="<{}".format("f"*len(data))
    bin=struct.pack(format,*data)
    f.write(bin)
    f.close()


def createMeta(nb,start,step,dir=dir):
    """
    create meta given :
    - a feed number
    - a unixtimestamp as start
    - a step
    """
    f=open("{}/{}.meta".format(dir,nb),"wb")
    data=np.array([0,0,step,start])
    format="<{}".format("I"*len(data))
    bin=struct.pack(format,*data)
    f.write(bin)
    f.close()


def newPHPFina(nb,start,step,data,dir=dir):
    """
    create a PHPFina object, without any reference to any EmonCMS server
    start : unix time stamp of the starting point
    step : timestep/interval in s
    data : data to be injected as a numpy vector
    """
    meta="{}/{}.meta".format(dir,nb)
    if os.path.isfile(meta) and os.path.getsize(meta) != 0:
        print("meta file exists")
        getMetas(nb,dir)
    else:
        print("creating meta")
        createMeta(nb,start,step,dir)
    if os.path.isfile("{}/{}.dat".format(dir,nb)):
        print("data file exists")
    else:
        print("creating data file")
        createFeed(nb,data,dir)


"""
création du tableau numpy initial pour le fonctionnement de la pompe :
"""

#il faut calculer le nombre de points depuis le début de l'instrumentation (pour avoir la size) :
#   - on calcule la différence entre maintenant et le début de l'expérience
#   ==> question : si les données arrivent en continu, faudra-t-il constamment remettre à jour l'unixtime de maintenant ??
#   - on le convertit en secondes
#   - on calcule combien de points sur cette durée (nb pts = durée / interval)

interval, starttime = getMetas(19) # température de départ circuit Sud
now = time.time()
duration = now - starttime
nb_pt = int(duration / interval)

pompe = np.ones(nb_pt)
newPHPFina(42, starttime, interval, pompe, dir)


## Test pour voir s'il crée bien un fichier ne contenant que des 1 :
#init = np.ones(10)  # à la place de 10, mettre la size du fichier meta
#createFeed(42, init, dir)
#f=open("{}/42.dat".format(dir),"r")
#f.close()
#print(lecture)
