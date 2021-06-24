import socket
import serial
import binascii
import logging
import time
import signal
#import json

#déclaration des variables gloables
port = 5000
size = 1024
signature = bytearray([0x44, 0xae, 0x0c])
sensorType = {0x01 : 'temp', 0x02 : 'tempRH', 0x03 : 'PT100', 0x04 : 'pulse', 0x05 : 'contact', 0x24 : 'CO2', 0x25 : '4_20mA', 0x26 : '0_5V', 0x27 : '0_10V'}
url = "192.168.2.1"
rcv = [0x21, 0x52, 0x09, 0x21]  # adresse du receveur
root = [0x7a, 0x5d, 0x00, 0x00, 0x00, 0x2f, 0x2f, 0x0f, 0x7f]


def decodeFrame(frame, log):
    # on reçoit le frame et on décode la mesure qu'il contient
    payload = {}
    sensorID = sensorType[frame[18]] # on détermine de quel type de capteur il s'agit
    log.debug('le capteur détecté est de type : {}'.format(sensorID))
    if sensorID == 'temp' or sensorID == 'tempRH' or sensorID == 'PT100':
        tempData = int.from_bytes(frame[21:23], byteorder = 'little', signed = True)/10
        payload['temp'] = tempData
        log.debug('température captée : {} °C'.format(tempData))
    if sensorID == 'tempRH':
        rhData = int.from_bytes(frame[23:25], byteorder = 'little')/10
        payload['rh'] = rhData
        log.debug('humidité relative : {} %'.format(rhData))
    if sensorID == 'CO2':
        co2Data = int.from_bytes(frame[21:23], byteorder = 'little')
        tempData = int.from_bytes(frame[23:25], byteorder = 'little', signed = True)/10
        rhData = int.from_bytes(frame[25:27], byteorder = 'little')/10
        payload['CO2'] = co2Data
        payload['temp'] = tempData
        payload['rh'] = rhData
        log.debug('taux de CO2 : {} ppm \n température captée : {} °C \n humidité relative : {} %'.format(co2Data, tempData, rhData))
    if sensorID == '4_20mA':
        currData = int.from_bytes(frame[21:23], byteorder = 'little')/100
        payload['current'] = currData
        log.debug('valeur du courant : {} mA'.format(currData))
    if sensorID == '0_5V' or sensorID == '0_10V':
        voltData = int.from_bytes(frame[21:23], byteorder = 'little')/100
        payload['voltage'] = voltData
        log.debug('valeur de tension : {} V'.format(voltData))
    return payload



class DataFlow:
    def __init__(self, interval, mode='socket'):
        self._exit = False
        self._interval = interval
        self._mode = mode
        self._log = logging.getLogger("enless")
        self._log.setLevel("DEBUG")
        self._log.debug("........OUVERTURE DU FIELD MANAGER........")

    def analysePaquet(self, frame):
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
                if l >=9 and frame[9] == 0x7a:
                    if l>= 14 and frame[12:14] == bytearray([0x01, 0x00]):
                        self._log.debug("message répété")
                    if frame[12:14] == bytearray([0x00, 0x00]):
                        self._log.debug("message direct")
                    if l>= 18 and frame[16:18] == bytearray([0x0f, 0x7f]):
                        if frame[18] == 0x10:
                            self._log.debug("requête d'installation en provenance de {}".format(sensorNbstr))
                            self.install(frame, self._interval)
                        if frame[18] == 0x12:
                            self._log.debug("paquet d'installation ACK reconnu")
                            self.RSSIresponse(frame)
                        if frame[18] == 0x14:
                            self._log.debug("paquet d'installation RSSI reconnu")
                            self.RSSIresponse(frame, nb=frame[20])
                        if frame[18] == 0x16:
                            self._log.debug('INSTALLATION EFFECTUÉE AVEC SUCCÈS')
                        if frame[18] in [0x01, 0x02, 0x03, 0x04, 0x23, 0x24, 0x25, 0x26, 0x27]:
                            self._log.debug('mesure à décoder')
                            decodeFrame(frame, self._log)

    def writePort(self, message):
        # on écrit un message sur le port série du router
        try:
            if self._mode == 'socket':
                #soc.close()  # on 'nettoie' la socket pour laisser la place à de nouvelles données
                n = self.s.send(message)
            if self._mode == 'serial':
                self.s.flushOutput()
                n = self.s.write(message)
        except IOError as e:
            self._log.error('ERROR {}'.format(e))
        finally:
            self._log.debug("wrote {} bytes on the serial port".format(n))

    def install(self, frame, interval):
        data = bytearray([0x11, frame[19], 0x01, *frame[3:7][::-1], interval, 0x00, *rcv[::-1]])
        length = len(root) + len(data)
        message = bytearray([length, *root, *data]) #on reconstruit le message envoyé au récepteur
        self._log.debug("Envoi du paquet d'installation")
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
            if self._mode == 'serial':
                with serial.serial_for_url("socket://{}:5000".format(url)) as self.s:
                    start = self.s.read(1)[0]
                    if start == 0x68:
                        #self._log.debug("mbus start flag")
                        length = self.s.read(1)[0]  # on lit le byte juste après, qui correspond à la longueur
                        frame = self.s.read(length)
                        stop = self.s.read(1)[0]
                        if stop == 0x16:
                            #self._log.debug(binascii.b2a_hex(frame))
                            self.analysePaquet(frame)
                            self._log.debug("**** fin du paquet ****")
            if self._mode == 'socket':
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.s:
                    self.s.connect((url, port))
                    start = self.s.recv(1)  # socket.recv = équivalent de serial.read
                    if start and start[0] == 0x68:
                        #self._log.debug("MBUS flag detected")
                        length = self.s.recv(1)[0]
                        frame = self.s.recv(length)
                        stop = self.s.recv(1)
                        if stop[0] == 0x16:
                            #self._log.debug(binascii.b2a_hex(frame))
                            self.analysePaquet(frame)
                            self._log.debug("**** fin du paquet ****")


    def _sigint_handler(self, signal, frame):
        # réception du signal de fermeture
        self._log.debug("signal de fermeture reçu")
        self._exit = True

    def close(self):
        #fermeture
        self._log.debug("fermeture")
        self.s.close()
        #if not self.s.is_open:  --> trouver l'équivalent pour la classe socket
        self._log.debug("port série fermé")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description = "Enless sniffer")
    parser.add_argument("--logfile", action="store")
    parser.add_argument("--conffile", action="store")
    args = parser.parse_args()

    # on initialise le journal avec le nom enless
    logger = logging.getLogger('enless')
    """
    on prévoit 2 cas :
    - journalisation dans un fichier
    - journalisation à l'écran
    """
    if args.logfile:
        print(args.logfile)
        import logging.handlers
        import os
        currentdir = os.path.abspath(os.getcwd())
        logfile = "{}/{}".format(currentdir,args.logfile)
        loghandler = logging.handlers.RotatingFileHandler(logfile, maxBytes=5000*1024, backupCount=1)
    else:
        loghandler = logging.StreamHandler()

    loghandler.setLevel("DEBUG")
    logger.addHandler(loghandler)
    loghandler.setFormatter(logging.Formatter("%(asctime) s %(levelname) 8s - %(message) s"))
    exemple = DataFlow(1, mode='serial')
    exemple.run(url)
    exemple.close()
