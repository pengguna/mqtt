import time
import json
import paho.mqtt.client as paho
from paho import mqtt

class MqttClient:

    def __init__(self, set_point, buffer = 0.1):
        self.set_point = set_point
        self.buffer = buffer 
        self.startup()

    def startup(self):
        client = paho.Client(client_id="heat_monitor", userdata=None, protocol=paho.MQTTv5)

        client.on_connect = self.on_connect
        client.on_subscribe = self.on_subscribe
        client.on_message = self.on_message
        #client.on_publish = self.on_publish

        client.username_pw_set("heat_monitor", "rawrxd")
        client.connect("192.168.0.36", 1883)

        self.client = client

        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc, properties=None):
        print("CONNACK received with code %s." % rc)

        # if we reconnect, we need to redo subs.
        client.subscribe("ferm_hot/#", qos=1)

    # with this callback you can see if your publish was successful
#    def on_publish(self, client, userdata, mid, properties=None):
        #        print("published? maybe")

    # print which topic was subscribed to
    def on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    # print message, useful for checking if it was successful
    def on_message(self, client, userdata, msg):
        if "SENSOR" in msg.topic:
            self.control_temp(json.loads(msg.payload))
        if "tele/STATE" in msg.topic: # dont want to pick up HASS_STATE
            self.update_state(json.loads(msg.payload))

    def update_state(self, data):
        if "POWER" not in data:
            print("ignoring state msg: ", data)
            return

        self.update_time = time.time()
        self.device_status = data["POWER"]

    def control_temp(self, data):
        if ("SI7021" not in data) or ("Temperature" not in data["SI7021"]):
            print("shit. bad payload: ", data)
            self.cache_publish("OFF")
            return

        cur_temp = data["SI7021"]["Temperature"]
        print("t=" + str(cur_temp))

        if cur_temp <= (self.set_point - self.buffer):
            self.cache_publish("ON")

        else:
            self._publish("OFF") # we should be smart and not publish if already off...

    def cache_publish(self, cmd):
        if (self.device_status != cmd):
            self._publish(cmd)

    def on_timeout(self):
        # TODO: work out how to trigger this bad boy...
        # we've not received data for 60s, something isn't right. we should kill it.
        print("Timeout, killing....")
        self._publish("OFF")

        # TODO: restart the timer.

    def _publish(self, cmd):

        print("publishing cmd:", cmd)
        # https://tasmota.github.io/docs/MQTT/#configure-mqtt-using-backlog
        # also just look at the info page for the device...
        self.client.publish("ferm_hot/cmnd/Power",payload=cmd, qos=1)


controller = MqttClient(20.4)

### TODO 
# 1. work out the timer and use that for timeout
# 2. work out how to deploy this guy to docker
# 3. get docker up and running
# 4. create an image with this file
# 5. pull and run it.
