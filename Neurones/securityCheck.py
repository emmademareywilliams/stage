import struct
import math
from dataengines import PyFina, getMeta

dir = "/var/opt/emoncms/phpfina"

def securityCheck(id, dir):
    """
    vérifie s'il y a présence de points aberrants dans la time serie
    (point aberrant <--> température > 100)
    id: numéro du flux à vérifier
    dir: chemin d'accès sur la machine pour obtenir le flux en question
    """
    meta = getMeta(id, dir)
    pos = 0
    i = 0
    nbn =0
    with open("{}/{}.dat".format(dir, id), "rb+") as ts:
        while pos <= meta["npoints"]:
            ts.seek(pos*4, 0)
            hexa = ts.read(4)
            aa = bytearray(hexa)
            if len(aa) == 4:
                value = struct.unpack('<f', aa)[0]
                if math.isnan(value):
                    nbn +=1
                elif value > 100:
                    print("valeur aberrante à {} : {}".format(pos, value))
                    i += 1
                    nv = struct.pack('<f', float('nan'))
                    try:
                        ts.seek(pos*4,0)
                        ts.write(nv)
                    except Exception as e:
                        print(e)
                    finally:
                        print("4 bytes written")
            pos +=1
        print("{} valeurs aberrantes".format(i))
        print("{} nan".format(nbn))

securityCheck(100, dir)
