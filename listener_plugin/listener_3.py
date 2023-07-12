# This plugin is set to connect to the websocket, subscribes to its plugion topic, and listens to 
# incoming notifications. 
# All the data is then sent to the Influx instance 

import json
from devicehive_plugin import Handler
from devicehive import Handler
from devicehive_plugin import Plugin
import influxdb_client, os
from influxdb_client import InfluxDBClient, Point, WritePrecision, BucketsApi
from influxdb_client.client.write_api import SYNCHRONOUS


script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

with open("config.json", "r") as f:
    config = json.load(f)

# chiavi influx
influx_user=config["influx_credentials"]["user"]
influx_password=config["influx_credentials"]["password"]
org = config["org"]
url_influx = config["url_influx"]

# il bucket contiene tutti i dati. Ha una data di scadenza deidibile dopo la quale i dati vengono cancellati
# si puo decidere di non cancellare mai i dati. Si possono avere piu bucket con regole diverse

# BUCKET KEYS
measures=config["bucket_keys"]["measurement"]
sens_name=config["bucket_keys"]["sensor_name"]

class SimpleHandler(Handler):

    def handle_connect(self):
        print('Successfully connected')
        
    def handle_event(self, event):
        print("event action:\n")
        print(event.action)
        if event.action=="notification/insert":
            self.n=1
        else:
            self.n=0
        print("event data:\n")
        print(type(event.data))

    def handle_command_insert(self, command): # will be called after command/insert event is received
        print("new device command created!\n")
        print(command.command)

    def handle_command_update(self, command): # will be called after command/update event is received
        print(command.command)

    def handle_notification(self, notification): # will be called after notification/insert event is received
        # print('notification:\n'+ notification.notification) = temperaturesensor("notification")

        device_id= notification.device_id
        
        verifica=notification.parameters #= dict{'humidity': 30, 'temperature1': 25.15, 'temperature2': 25.03}
        
        if self.n==1:  # if the action is to insert a notification
            parameter=notification.parameters
            for measurment in parameter.keys(): # here i call every type of measure in the dictionary
                # print("measurement:")
                # print(measurment)
                # print("values:")
                value=parameter[measurment] # nuova misura si registra in automatico
                # print(value)

                client = influxdb_client.InfluxDBClient(url=url_influx, username=influx_user, password=influx_password,org=org) 
                write_api = client.write_api(write_options=SYNCHRONOUS)
                Bclient = influxdb_client.BucketsApi(client)
                lista=Bclient.find_buckets() #lista buckets
                lista_dict=lista.to_dict()

                self.bucket=f"{device_id}"
                bb=lista_dict['buckets']
                names = [bucket['name'] for bucket in bb]
                print(names) #nomi dei buckets
                old=Bclient.find_bucket_by_name(self.bucket) # current bucket

                # alterantive: if names in not none (names = dict con tutti i nomi)
                if old is None:
                    t=config['retention_time'] 
                    bucket=Bclient.create_bucket(None,self.bucket,org , {"everySeconds": t}, 'Bucket with one week retention')
                    # if no bucket exists create a new one

                point=Point(measures).tag(sens_name,device_id).field(measurment,value)
                write_api.write(bucket=self.bucket, org=org, record=point)

plugin=config["plugin"]
url = plugin["url"]
topic_name = plugin["topic_name"]
auth_url = plugin["auth_url"]

dh_credentials=config["dh_credentials"]

plugin = Plugin(SimpleHandler)
plugin.connect(url, topic_name, auth_url=auth_url, login=dh_credentials["user"], password=dh_credentials["password"])

