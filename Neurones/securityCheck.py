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
    with open("{}/{}.dat".format(dir, id), "rb") as ts:
        ts.seek(pos*4, 0)
        hexa = ts.read(4)
        aa = bytearray(hexa)
        if len(aa) == 4:
            value = struct.unpack('<f', aa)[0]
            if not(math.isnan(value)) and value > 100:
                print("valeur aberrante à {}".format(pos))
            else:
                print("tout va bien :-)")
        pos +=1

securityCheck(9, dir)
