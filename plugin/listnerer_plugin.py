import paho.mqtt.client as mqtt
import uuid
import json
import time
from devicehive_plugin import Handler
from devicehive_plugin import Plugin

old=0
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
        print('parametro:\n') 
        print(notification.parameters)
        

url = 'ws://francesco-legion-5-15ach6h/plugin/proxy/'
topic_name = 'plugin_topic_27e39a6e-5dac-4d36-83b3-d2785c92d7f9' 
auth_url = 'http://francesco-legion-5-15ach6h/api/rest'

plugin = Plugin(SimpleHandler)
# plugin.connect(url, topic_name, plugin_access_token=plugin_access_token)
plugin.connect(url, topic_name, auth_url=auth_url,
               login='dhadmin', password='dhadmin_#911')
