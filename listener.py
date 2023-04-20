import uuid
import json
import time
import paho.mqtt.client as mqtt


ACCESS_TOKEN ='eyJhbGciOiJIUzI1NiJ9.eyJwYXlsb2FkIjp7ImEiOlswXSwiZSI6MjAwMTExMDQwMDAwMCwidCI6MSwidSI6MSwibiI6WyIqIl0sImR0IjpbIioiXX19.R1mEe2j6P8r_Mt_yjVFieIweXzVDM6CihGQgvBTk6gs'
BROKER = 'francesco-legion-5-15ach6h'
LATENCY= 5 # ascolta e manda ogni 5 secondi
i = 0

class Listener(object):

    def __init__(self, url, access_token): #TOOK AWAY ID
        self._client_id = str(uuid.uuid4())
        self._connected = False
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
                self._connected = True
            else:
                print("Failed to authenticate.")

    def _on_disconnect(self, client, userdata, rc):
        print('Disconnected with rc=%s' % rc)
        self._connected = False
    
    def _publish(self, topic, payload):
        payload['requestId'] = str(uuid.uuid4())
        self._client.publish(topic, json.dumps(payload))
        print(f"{payload} published!/n/n")

    def listen(self, topic, message):
        self._client.subscribe(topic)
        js=json.load(message)
        if js['time'] != old_time:
            old_time=js['time']
            print (js)

    def run(self):
        while not self._connected:
            time.sleep(0.01)
        time.sleep(1.0)

        while self._connected:
            dht_1={"time":time.time(),'value':i}
            Jdht_1=json.dump(dht_1)
            self.publish('dh/sensor_data/dht_1',dht_1)
            i=i+1
            dht_2={"time":time.time(),'value':i}
            Jdht_1=json.dump(dht_2)
            self.publish('dh/sensor_data/dht_2',dht_2)
            
            time.sleep(LATENCY)

if __name__ == '__main__':
    i=0
    old_time=0
    d = Listener(BROKER, ACCESS_TOKEN)
    d.run()

