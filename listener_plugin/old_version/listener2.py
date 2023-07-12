# This plugin is set to connect to the websocket, subscribes to its plugion topic, and listens to 
# incoming notifications. 
# All the data is then sent to the Influx instance 

import paho.mqtt.client as mqtt
import json
from devicehive_plugin import Handler
from devicehive import Handler
from devicehive_plugin import Plugin
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision, BucketsApi
from influxdb_client.client.write_api import SYNCHRONOUS
from dateutil import parser

user='francescogaggini'
password='dxzr5962'

org = "aquaseek"
url_influx = "http://francesco-legion-5-15ach6h:8086"
bucket='machine_a' # il bucket contiene tutti i dati. Ha una data di scadenza deidibile dopo la quale i dati vengono cancellati
# si puo decidere di non cancellare mai i dati. Si possono avere piu bucket con regole diverse

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
        # print('device id:\n'+ device_id)
        verifica=notification.parameters #= dict{'humidity': 30, 'temperature1': 25.15, 'temperature2': 25.03}
        
        if self.n==1:  # if the action is to insert a notification
            parameter=notification.parameters
            for measurment in parameter.keys(): # here i call every type of measure in the dictionary
                # print("measurement:")
                # print(measurment)
                # print("values:")
                value=parameter[measurment]
                # print(value)

                client = influxdb_client.InfluxDBClient(url=url_influx, username=user, password=password,org=org) 
                write_api = client.write_api(write_options=SYNCHRONOUS)
                Bclient = influxdb_client.BucketsApi(client)
                lista=Bclient.find_buckets()
                print("lista buckets:::::::::::::::::::::::::")
                lista_dict=lista.to_dict()
                #print(lista)
                self.bucket='machine_a'#+self.b # 1 2 3...
                bb=lista_dict['buckets']
                names = [bucket['name'] for bucket in bb]
                print(names) #ARRIVATO A : ho i nomi dei buckets
                old=Bclient.find_bucket_by_name(self.bucket) # current bucket

                # alterantive: if names in not none (names= dict con tutti i nomi)
                if old is None: 
                    bucket=Bclient.create_bucket(None,self.bucket,'aquaseek', {"everySeconds": 604800}, 'Bucket with one week retention')
                    # if no bucket exists create a new one

                point=Point('measurement').tag('sensor_name',device_id).field(measurment,value)
                write_api.write(bucket=self.bucket, org=org, record=point)

url = 'ws://francesco-legion-5-15ach6h/plugin/proxy/'
topic_name = 'plugin_topic_27e39a6e-5dac-4d36-83b3-d2785c92d7f9' 
auth_url = 'http://francesco-legion-5-15ach6h/api/rest'

plugin = Plugin(SimpleHandler)
plugin.connect(url, topic_name, auth_url=auth_url,
               login='dhadmin', password='dhadmin_#911')

