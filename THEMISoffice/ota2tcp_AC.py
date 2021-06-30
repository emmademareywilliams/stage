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
    
    retourne :
    - le payload à publier sur le broker MQTT
    - un message pour le log
    """
    payload = {}
    message = None
    sensorID = sensorTypes[frame[18]] # on détermine le type de capteur
    log.debug('le capteur détecté est de type : {}'.format(sensorID))
    
    if sensorID in ['temp', 'tempRH', 'PT100'] and len(frame)>=23:
        tempData = int.from_bytes(frame[21:23], byteorder = 'little', signed = True)/10
        payload['temp'] = tempData
        message = 'température : {} °C'.format(tempData)
    
    if sensorID == 'tempRH' and len(frame)>=25:
        rhData = int.from_bytes(frame[23:25], byteorder = 'little')/10
        payload['rh'] = rhData
        message = 'HR : {} %'.format(rhData)
    
    if sensorID == 'CO2' and len(frame)>=27:
        co2Data = int.from_bytes(frame[21:23], byteorder = 'little')
        tempData = int.from_bytes(frame[23:25], byteorder = 'little', signed = True)/10
        rhData = int.from_bytes(frame[25:27], byteorder = 'little')/10
        payload['CO2'] = co2Data
        payload['temp'] = tempData
        payload['rh'] = rhData
        message = 'taux de CO2 : {} ppm \n température : {} °C \n HR : {} %'.format(co2Data, tempData, rhData)
    
    if sensorID == '4_20mA' and len(frame)>=23:
        currData = int.from_bytes(frame[21:23], byteorder = 'little')/100
        payload['current'] = currData
        message = 'valeur du courant : {} mA'.format(currData)
    
    if sensorID in ['0_5V', '0_10V'] and len(frame)>=23:
        voltData = int.from_bytes(frame[21:23], byteorder = 'little')/100
        payload['voltage'] = voltData
        message = 'valeur de tension : {} V'.format(voltData)
    
    if len(frame) == length :
        payload["rssi"] = frame[-1]/2
        payload["battery status"] = frame[-2]
    
    return payload, message


class DataFlow:
    def __init__(self, conf):
        self._exit = False
        self._conf = conf
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
                            interval = 5
                            if self._conf:
                                if "numbers" in self._conf:
                                    interval = conf["interval"]
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
                        
                        if frame[18] in sensorTypes :
                            # on évalue si on doit traiter les données
                            publish = False
                            if self._conf:
                                if "numbers" in self._conf:
                                    if sensorNbstr in self._conf["numbers"]:
                                        publish=True
                                else:
                                    publish=True
                            
                            # on décode et on publie les infos du capteur dans Emoncms :        
                            if publish:
                                self._log.debug('mesure à décoder')
                                payload, message = decodeFrame(frame, length)
                                if message:
                                    self._log.debug(message)
                                payload['repeated'] = repeated
                                msg = publishToMQTT(sensorNbstr, payload)
                                if msg["success"]:
                                    self._log.debug(msg["text"])
                                else:
                                    self._log.error(msg["text"])

    def writePort(self, message):
        # écrit un message sur le port série du router
        try:
            #self.s.close()  # on 'nettoie' la socket pour laisser la place à de nouvelles données
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
        self.writePort(message)

    def RSSIresponse(self, frame, nb=0x01):
        data = bytearray([0x15, frame[19], nb, *frame[3:7][::-1], frame[-1]])
        length = len(root) + len(data)
        message = bytearray([length, *root, *data])
        self._log.debug("Envoi de la réponse RSSI {:02x}".format(nb))
        self.writePort(message)


    def run(self, url):
        signal.signal(signal.SIGINT, self._sigint_handler)
        signal.signal(signal.SIGTERM, self._sigint_handler)
        while not self._exit:
            start = None
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.s:
                self.s.connect((url, port))
                start = self.s.recv(1)  # socket.recv = équivalent de serial.read
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
            time.sleep(0.1)


    def _sigint_handler(self, signal, frame):
        # réception du signal de fermeture
        self._log.debug("signal de fermeture reçu")
        self._exit = True

    def close(self):
        #fermeture
        self._log.debug("fermeture")
        self.s.close()
        self._log.debug("port série fermé")


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
    """
    on prévoit 2 cas :
    - journalisation dans un fichier
    - journalisation à l'écran
    """
    if args.log:
        print(args.log)
        import logging.handlers
        loghandler = logging.handlers.RotatingFileHandler(args.log, maxBytes=5000*1024, backupCount=1)
    else:
        loghandler = logging.StreamHandler()
    loghandler.setLevel("DEBUG")
    logger.addHandler(loghandler)
    loghandler.setFormatter(logging.Formatter("%(asctime) s %(levelname) 8s - %(message) s"))
    """
    initialisation du fichier conf
    si conf vaut None, aucune mesure ne sera envoyée vers emoncms
    """
    conf = None
    try:
        with open(args.conf) as f:
            conf =  json.loads(f.read())
    except Exception as e:
        logger.error("fichier de configuration mal formé %s", e)

    sniffer = DataFlow(conf)
    sniffer.run(url)
    sniffer.close()
