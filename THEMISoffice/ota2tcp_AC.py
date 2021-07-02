#!/usr/bin/env python3

import socket
import binascii
import logging
import time
import signal
from mqttTools import *

#déclaration des variables globales
signature = bytearray([0x44, 0xae, 0x0c])
root = [0x7a, 0x5d, 0x00, 0x00, 0x00, 0x2f, 0x2f, 0x0f, 0x7f]

sensorTypes = {
    0x01 : 'temp', 0x02 : 'tempRH', 0x03 : 'PT100', 
    0x04 : 'pulse', 0x05 : 'contact', 0x24 : 'CO2', 
    0x25 : '4_20mA', 0x26 : '0_5V', 0x27 : '0_10V'
    }

port = 5000
url = "192.168.2.1"
rcv = [0x20, 0x52, 0x18, 0x05]  # adresse du receveur sans effet (?) --> à voir avec support technique


def decodeFrame(frame, length):
    """
    on décode la mesure
    
    frame : message mbus wireless sans l'octet de start, la longueur et l'octet de fin
    
    retourne le payload à publier sur le broker MQTT
    """
    payload = {}
    sensorID = sensorTypes[frame[18]] # on détermine le type de capteur
    
    if sensorID in ['temp', 'tempRH', 'PT100'] and len(frame)>=23:
        temp = int.from_bytes(frame[21:23], byteorder = 'little', signed = True)/10
        payload['temp'] = temp
    
    if sensorID == 'tempRH' and len(frame)>=25:
        rh = int.from_bytes(frame[23:25], byteorder = 'little')/10
        payload['rh'] = rh
    
    if sensorID == 'CO2' and len(frame)>=27:
        co2 = int.from_bytes(frame[21:23], byteorder = 'little')
        temp = int.from_bytes(frame[23:25], byteorder = 'little', signed = True)/10
        rh = int.from_bytes(frame[25:27], byteorder = 'little')/10
        payload['CO2'] = co2
        payload['temp'] = temp
        payload['rh'] = rh
    
    if sensorID == '4_20mA' and len(frame)>=23:
        curr = int.from_bytes(frame[21:23], byteorder = 'little')/100
        payload['current'] = curr
    
    if sensorID in ['0_5V', '0_10V'] and len(frame)>=23:
        volt = int.from_bytes(frame[21:23], byteorder = 'little')/100
        payload['voltage'] = volt
    
    if len(frame) == length :
        payload["rssi"] = frame[-1]/2
        payload["battery status"] = frame[-2]
    
    return payload


class DataFlow:
    def __init__(self, confname):
        self._exit = False
        self._confname = confname
        self._log = logging.getLogger("enless")
        self._log.setLevel("DEBUG")
        self._log.debug("........OUVERTURE DU FIELD MANAGER........")

    def analysePaquet(self, frame, length):
        """
        frame : message mbus wireless sans l'octet de start, la longueur et l'octet de fin
        """
        l = len(frame)
        if l >= 3 and frame[0:3] == signature:
            self._log.debug("capteur Enless détecté")
            if l >= 7 :
                sensorNb = frame[3:7][::-1]
                sensorNbstr = "{:02x}{:02x}{:02x}{:02x}".format(*sensorNb)
                self._log.debug("numéro de série : {}".format(sensorNbstr))
                repeated = 0
                if l >=10 and frame[9] == 0x7a:
                    if l>= 14:
                        if frame[12:14] == bytearray([0x01, 0x00]):
                            self._log.debug("message répété")
                            repeated = 1
                        if frame[12:14] == bytearray([0x00, 0x00]):
                            self._log.debug("message direct")
                    
                    if l>= 21 and frame[16:18] == bytearray([0x0f, 0x7f]):
                        if frame[18] == 0x10:
                            self._log.debug("requête d'installation en provenance de {}".format(sensorNbstr))
                            interval = self._conf["interval"]
                            if frame[19] == 0x24:
                                interval = 3 * interval
                            self.install(frame, interval)
                        
                        if frame[18] == 0x12:
                            self._log.debug("paquet d'installation ACK reconnu")
                            self.RSSIresponse(frame)
                        
                        if frame[18] == 0x14:
                            self._log.debug("paquet d'installation RSSI reconnu")
                            self.RSSIresponse(frame, nb=frame[20])
                        
                        if frame[18] == 0x16:
                            self._log.debug('INSTALLATION EFFECTUÉE AVEC SUCCÈS')
                            #injection du numéro de capteur dans le fichier conf
                            # à ce stade, le fichier conf existe forcément
                            with open(self._confname, "r+") as f:
                                conf = json.load(f)
                                if "numbers" not in conf:
                                    conf["numbers"] = []
                                if sensorNbstr not in conf["numbers"]:
                                    conf["numbers"].append(sensorNbstr)
                                f.seek(0)
                                json.dump(conf, f, indent=4)
                        
                        if frame[18] in sensorTypes :
                            # doit-on traiter les données ?
                            publish = True
                            if "numbers" in self._conf:
                                if sensorNbstr not in self._conf["numbers"]:
                                    publish=False
                            
                            # on décode et on publie les infos du capteur dans Emoncms :        
                            if publish:
                                self._log.debug('mesure à décoder')
                                payload = decodeFrame(frame, length)
                                if payload:
                                    self._log.debug(payload)
                                payload['repeated'] = repeated
                                msg = publishToMQTT(sensorNbstr, payload)
                                if msg["success"]:
                                    self._log.debug(msg["text"])
                                else:
                                    self._log.error(msg["text"])

    def write(self, message):
        """
        écrit un message sur la socket qui a été utilisée en lecture
        l'appel à write doit être réalisé au sein du with de run() 
        """
        try:
            n = self.s.send(message)
        except IOError as e:
            self._log.error('ERROR {}'.format(e))
        else:
            self._log.debug("{} bytes written".format(n))

    def install(self, frame, interval):
        data = bytearray([0x11, frame[19], 0x01, *frame[3:7][::-1], interval, 0x00, *rcv[::-1]])
        length = len(root) + len(data)
        message = bytearray([length, *root, *data]) #on reconstruit le message envoyé au récepteur
        self._log.debug("Envoi du paquet d'installation")
        self._log.debug(binascii.b2a_hex(message))
        self.write(message)

    def RSSIresponse(self, frame, nb=0x01):
        data = bytearray([0x15, frame[19], nb, *frame[3:7][::-1], frame[-1]])
        length = len(root) + len(data)
        message = bytearray([length, *root, *data])
        self._log.debug("Envoi de la réponse RSSI {:02x}".format(nb))
        self.write(message)


    def run(self, url, port):
        signal.signal(signal.SIGINT, self._sigint_handler)
        signal.signal(signal.SIGTERM, self._sigint_handler)
        
        # conf par défault
        if not self._exit:
            self._conf = {"interval":5}
            
        while not self._exit:
            
            # prise en compte des modifs de configuration
            # si le fichier conf n'existe pas, on sort du programme
            try:
                with open(self._confname) as f:
                    conf =  json.loads(f.read())
                    if "interval" not in conf:
                        conf["interval"] = 5
                    if conf != self._conf:
                        self._conf = conf
            except Exception as e:
                self._log.debug(e)
                self._exit = True
                break

            start = None
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.s:
                self.s.connect((url, port))
                self.s.settimeout(5)
                try:
                    start = self.s.recv(1)
                except Exception as e:
                    self._log.warning(e)
                else:
                    if start and start[0] == 0x68:
                        #self._log.debug("MBUS flag detected")
                        length = self.s.recv(1)[0]
                        frame = self.s.recv(length)
                        stop = self.s.recv(1)[0]
                        if stop == 0x16:
                            self._log.debug("0x16 détecté - paquet complet")
                        if frame:
                            self._log.debug(binascii.b2a_hex(frame))
                            self.analysePaquet(frame, length)
                            self._log.debug("******************")
                finally:
                    self.s.close()
            time.sleep(0.1)


    def _sigint_handler(self, signal, frame):
        # réception du signal de fermeture
        self._log.debug("signal de fermeture reçu")
        self._exit = True

    def close(self):
        #fermeture
        self._log.debug("fermeture")


if __name__ == "__main__":
    import argparse
    import json
    import sys
    parser = argparse.ArgumentParser(description = "Enless sniffer")
    parser.add_argument("--log", action="store")
    parser.add_argument("--conf", action="store", default="{}/ota2tcp.conf".format(sys.path[0]))
    args = parser.parse_args()

    # on initialise le journal avec le nom enless :
    logger = logging.getLogger('enless')
    if args.log:
        # journalisation dans un fichier
        import logging.handlers
        loghandler = logging.handlers.RotatingFileHandler(args.log, maxBytes=5000*1024, backupCount=1)
    else:
        # journalisation à l'écran
        loghandler = logging.StreamHandler()
    loghandler.setLevel("DEBUG")
    logger.addHandler(loghandler)
    loghandler.setFormatter(logging.Formatter("%(asctime) s %(levelname) 8s - %(message) s"))
    
    if args.conf:
        enless = DataFlow(args.conf)
    else:
        enless = DataFlow("ota2tcp.conf")
    enless.run(url, port)
    enless.close()
