# This plugin is set to connect to the websocket, subscribes to its plugion topic, and listens to 
# incoming notifications. 
# All the data is then sent to the Influx instance 
#

import paho.mqtt.client as mqtt
from devicehive_plugin import Handler
from devicehive_plugin import Plugin
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dateutil import parser
token = 'SkmJM1EVrXzLmZLE6K1RntVWg8AHaPsSYAbgRR74BOxN1Rlrm9NeXK5K78HdmHb41jx68RmlmSPP8DJVX6bIHg=='
org = "aquaseek"
url_influx = "http://francesco-legion-5-15ach6h:8086"
bucket='machine_a'

class SimpleHandler(Handler):
    def handle_connect(self):
        print('Successfully connected')
        
    def handle_event(self, event):
        print(event.action)
        print(type(event.data))

    def handle_command_insert(self, command): # will be called after command/insert event is received
        print(command.command)

    def handle_command_update(self, command): # will be called after command/update event is received
        print(command.command)

    def handle_notification(self, notification): # will be called after notification/insert event is received
        print('notifica:\n'+ notification.notification)
        print('timestamp:\n'+ notification.timestamp)
        
        device_id=notification.device_id
        print('device id:\n'+ device_id)
        
        parameter=notification.parameters
        temperature=parameter['temperature']
        print('parameter:') 
        print(temperature)

        client = influxdb_client.InfluxDBClient(url=url_influx, token=token, org=org)
        write_api = client.write_api(write_options=SYNCHRONOUS)

        point=Point('measurement').tag('sensor_name',device_id).field('temperature',temperature)
        write_api.write(bucket=bucket, org=org, record=point)

url = 'ws://francesco-legion-5-15ach6h/plugin/proxy/'
topic_name = 'plugin_topic_27e39a6e-5dac-4d36-83b3-d2785c92d7f9' 
auth_url = 'http://francesco-legion-5-15ach6h/api/rest'

plugin = Plugin(SimpleHandler)
plugin.connect(url, topic_name, auth_url=auth_url,
               login='dhadmin', password='dhadmin_#911')
