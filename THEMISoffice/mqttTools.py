import paho.mqtt.client as mqtt
import json

# user et passwd ne servent pas vu qu'on est sur un script local
mqtt_user = "emonpi"
mqtt_passwd = "emonpimqtt2016"
mqtt_host = "127.0.0.1"
mqtt_port = 1883
mqttc = mqtt.Client()
mqttc.username_pw_set(mqtt_user, mqtt_passwd)

def publishToMQTT(node, payload):
    """
    se connecte au broker mqtt et envoie un payload json
    """
    message = {}
    message["success"] = True
    try:
        mqttc.connect(mqtt_host, mqtt_port, 60)
    except Exception:
        message["success"] = False
        message["text"] = "Could not connect to MQTT"
    else:
        text = "Connected to MQTT and sending to node {}".format(node)
        payloadJSON = json.dumps(payload)
        result = mqttc.publish("emon/{}".format(node), payloadJSON)
        if result[0] != 0 :
            message["success"] = False
            text = "{} Error {}".format(text, result)
        mqttc.disconnect()
        message["text"] = text
    return message
