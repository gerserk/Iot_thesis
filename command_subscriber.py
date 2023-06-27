import uuid
import json
import time
import random

import paho.mqtt.client as mqtt

SERVER_HOST = 'francesco-legion-5-15ach6h'
ACCESS_TOKEN ='eyJhbGciOiJIUzI1NiJ9.eyJwYXlsb2FkIjp7ImEiOlswXSwiZSI6MjAxOTYwMDAwMDAwMCwidCI6MSwidSI6MSwibiI6WyIqIl0sImR0IjpbIioiXX19.k_e_eKEj6EciONMcx-AgaGnbENNla2aecaS0TO44ga4'
DEVICE_ID = 'mqtt-demo-device-' + ACCESS_TOKEN[0:4]
LATENCY = 10 #send measurements every N seconds
NETWORK_ID= 1 #To be obtained...
DEVICETYPE_ID= 1 #To be obtained...

class MQTTDemo(object):

    def __init__(self, url, access_token, device_id):
        self._client_id = str(uuid.uuid4())
        self._connected = False
        self._device_id = device_id
        self._accessToken = access_token

        self._client = mqtt.Client(self._client_id)
        self._client.connect(url)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect
        self._client.loop_start()

    def _on_connect(self, client, userdata, flags, rc):
        print('Connected with rc=%s' % rc)
        client.subscribe('dh/response/authenticate@%s' % self._client_id)
        self._publish('dh/request', {
            'action': 'authenticate',
            'token': self._accessToken,
            'requestId': str(uuid.uuid4())
        })

    def _on_message(self, client, userdata, message):
        print('New message: %s' % message.payload)
        js = json.loads(message.payload)
        if js['action'] == 'authenticate':
            if js['status'] == 'success':
                client.subscribe('dh/response/device/save@%s' % self._client_id)
                client.subscribe('dh/response/notification/insert@%s' % self._client_id)
                #client.subscribe('dh/command/#') #receives all commands.. not desired..
                client.subscribe(f'dh/command/{NETWORK_ID}/{DEVICETYPE_ID}/{DEVICE_ID}/#') #MAYBE SUBSCRIBE TO PARTICULAR DEVICE COMMANDS...
                self._connected = True
            else:
                print("Failed to authenticate.")
        if js['action'] == 'notification/subscribe':
            command=js['command']
            print(command['parameters'])

    def _on_disconnect(self, client, userdata, rc):
        print('Disconnected with rc=%s' % rc)
        self._connected = False

    def _publish(self, topic, payload):
        payload['requestId'] = str(uuid.uuid4())
        self._client.publish(topic, json.dumps(payload))

    def run(self):
        while not self._connected:
            time.sleep(0.01)
        time.sleep(1.0)
        while self._connected:
            time.sleep(LATENCY)
            
            


if __name__ == '__main__':
    d = MQTTDemo(SERVER_HOST, ACCESS_TOKEN, DEVICE_ID)
    d.run()