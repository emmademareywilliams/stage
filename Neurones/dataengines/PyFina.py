import numpy as np
import struct
import os
import math
try:
    import matplotlib.pylab as plt
    matplotlib_found = True
except ImportError:
    matplotlib_found = False

def getMeta(id, dir):
    """
    decoding the .meta file

    id (4 bytes, Unsigned integer)
    npoints (4 bytes, Unsigned integer, Legacy : use instead filesize//4 )
    interval (4 bytes, Unsigned integer)
    start_time (4 bytes, Unsigned integer)

    """
    with open("{}/{}.meta".format(dir,id),"rb") as f:
        f.seek(8,0)
        hexa = f.read(8)
        aa= bytearray(hexa)
        if len(aa)==8:
            decoded=struct.unpack('<2I', aa)
        else:
            print("corrupted meta - aborting")
            return False
    meta = {
             "interval":decoded[0],
             "start_time":decoded[1],
             "npoints":os.path.getsize("{}/{}.dat".format(dir,id))//4
           }
    return meta

class PyFina(np.ndarray):

    def __new__(cls, id, dir, start, step, npts):
        meta = getMeta(id, dir)
        if not meta:
            return
        """
        decoding and sampling the .dat file
        values are 32 bit floats, stored on 4 bytes
        to estimate value(time), position in the dat file is calculated as follow :
        pos = (time - meta["start_time"]) // meta["interval"]
        Nota : no NAN value - if a NAN is detected, the algorithm will fetch the first non NAN value in the future
        """
        verbose = False
        obj = np.zeros(npts).view(cls)

        end = start + (npts-1) * step
        time = start
        i = 0
        with open("{}/{}.dat".format(dir,id), "rb") as ts:
            while time < end:
                time = start + step * i
                pos = (time - meta["start_time"]) // meta["interval"]
                if pos >=0 and pos < meta["npoints"]:
                    #print("trying to find point {} going to index {}".format(i,pos))
                    ts.seek(pos*4, 0)
                    hexa = ts.read(4)
                    aa= bytearray(hexa)
                    if len(aa)==4:
                      value=struct.unpack('<f', aa)[0]
                      if not math.isnan(value):
                          obj[i] = value
                      else:
                          if verbose:
                              print("NAN at pos {} uts {}".format(pos, meta["start_time"]+pos*meta["interval"]))
                          j=1
                          while True:
                              #print(j)
                              ramble=(pos+j)*4
                              ts.seek(ramble, 0)
                              hexa = ts.read(4)
                              aa= bytearray(hexa)
                              value=struct.unpack('<f', aa)[0]
                              if math.isnan(value):
                                  j+=1
                              else:
                                  break
                          obj[i] = value
                    else:
                      print("unpacking problem {} len is {} position is {}".format(i,len(aa),position))
                i += 1
        """
        storing the "signature" of the "sampled" feed
        """
        obj.start = start
        obj.step = step

        return obj

    def __array_finalize__(self, obj):
        if obj is None: return
        self.start = getattr(obj, 'start', None)
        self.step = getattr(obj, 'step', None)

    def timescale(self):
        """
        return the time scale of the feed as a numpy array
        """
        return np.arange(0,self.step*self.shape[0],self.step)

Cw = 1162.5 #Wh/m3/K

def prepare(dir, start, step, nb, **kwargs):
    """
    Fonction assez g??n??rique qui pr??pare
    les donn??es historiques 'FROIDES' pour les mod??les
    Renvoie 3 objets PyFina :
    - la puissance de chauffage Qc,
    - les temp??ratures ext??rieures et int??rieures, Text et Tint

    Parmi les param??tres optionnels, il faut donner :
    - les num??ros de flux de Text, Tint
    - la valeur du d??bit en m3/h
    - les num??ros de flux de Tdep, Tret, ou la valeur du deltaT

    Enfin, l'algo a besoin de savoir quant a lieu la distribution de chaleur
    soit on donne pompe ON/OFF=0/1 dans les arguments
    soit on donne autopilot = mode de fonctionnement du r??gulateur t??l??command?? par BIOS
    liste non exhaustive des modes que l'on peut rencontrer sur un r??gulateur standard :
    - standby/antigel
    - ??t??/antigel
    - chauffage permanent normal/antigel selon programme horaire
    - chauffage permanent normal/r??duit selon programme horaire
    - chauffage permanent normal
    - chauffage permanent r??duit
    """

    if "Text" not in kwargs or "Tint" not in kwargs:
        return False

    Text = PyFina(kwargs["Text"], dir, start, step, nb)
    Tint = PyFina(kwargs["Tint"], dir, start, step, nb)

    if "flow_rate" not in kwargs:
        print("flow_rate is missing - please give it in m3/h")
        return False

    flow_rate = kwargs["flow_rate"]

    # il faut un champ 0/1 qui indique quant le relais est activ?? ou non
    if "pompe" in kwargs:
        heating = PyFina(kwargs['pompe'], dir, start, step, nb)
    elif "autopilot" in kwargs:
        autopilot = PyFina(kwargs['autopilot'], dir, start, step, nb)
        #  ?? priori, la valeur minimale dans l'autopilot repr??sente l'arr??t du syst??me de chauffage
        # c'est ainsi sur presque tous les syst??mes,
        lower = np.min(autopilot)
        tmp = lower * np.ones(nb)
        heating = (autopilot - tmp)
        upper = np.max(heating)
        heating = heating / upper

    graphid = 211

    if "Tdep" in kwargs and "Tret" in kwargs:
        Tdep = PyFina(kwargs['Tdep'], dir, start, step, nb)
        Tret = PyFina(kwargs['Tret'], dir, start, step, nb)
        Qc = heating * flow_rate * Cw * np.maximum(Tdep - Tret,np.zeros(nb))
        graphid += 200
    elif "deltaT" in kwargs:
        # si on a pas les temp??ratures de circuit, on peut fournir un deltaT
        Qc = heating * flow_rate * Cw * kwargs['deltaT']
    else:
        # si on ne fournit aucune info, on prend forfaitairement un deltaT de 15 ??C
        # attention, sur certaines installations tr??s bien r??gl??es, c'est plut??t 5
        # mais sur ces installations, on aura Tdep et Tret sans soucis :-)
        Qc = heating * flow_rate * Cw * 15

    preview = True
    if "nopreview" in kwargs:
        preview = not kwargs['nopreview']

    if matplotlib_found and preview:
        from planning import tsToHuman
        ax1=plt.subplot(graphid)
        plt.title("prepa. donn??es circuit {} - {}".format(kwargs["Tint"], tsToHuman(start)))
        plt.plot(Tint, color="green", label="Tint mesur??e")
        plt.legend(loc="upper left")
        ax2=ax1.twinx()
        ax2=plt.plot(heating, label="pompe ON/OFF ou autopilot")
        plt.legend(loc="upper right")
        graphid+=1
        ax3=plt.subplot(graphid)
        plt.plot(Qc, color="red", label="heating power (W)")
        plt.fill_between(np.arange(nb),0, Qc, color="#fff2ce")
        plt.legend(loc="upper right")
        ax4=ax3.twinx()
        plt.plot(Text, label="Text")
        plt.legend(loc="upper left")
        if "Tdep" in kwargs and "Tret" in kwargs:

            _Tdep = Tdep * heating
            _Tret = Tret * heating
            Tdep_clean = _Tdep[_Tdep[:]>0]
            Tret_clean = _Tret[_Tdep[:]>0]
            #coeffs = np.polyfit(Tdep * heating, Tret * heating, 1)
            if Tdep_clean.shape[0] and Tret_clean.shape[0]:
                graphid+=1
                coeffs = np.polyfit(Tdep_clean, Tret_clean, 1)
                ax5=plt.subplot(graphid)
                ax5.set_ylabel("??C")
                Tret_sim = coeffs[0] * Tdep_clean + coeffs[1]
                plt.plot(Tdep*heating,Tret*heating, '*', label="Tret={:.2f}*Tdep + {:.2f}".format(coeffs[0],coeffs[1]))
                plt.plot(Tdep_clean, Tret_sim)
                plt.legend()

            # diff??rentiel entre circuit et ambiance int??rieure
            diff = Tdep_clean-Tint[heating[:]==1]
            deltaT = Tdep_clean-Tret_clean
            if diff.shape[0] and deltaT.shape[0]:
                graphid+=1
                coeffs = np.polyfit(diff, deltaT, 1)
                plt.subplot(graphid)
                plt.ylabel("dT circuit ??C")
                plt.xlabel("diff??rentiel de temp??rature entre circuit et int??rieur ??C")
                plt.plot( diff, deltaT, '*', label="dT = {:.2f} + diff*{:.2f}".format(coeffs[1], coeffs[0]))
                plt.legend()
                
        plt.show()

    return Qc, Text, Tint
