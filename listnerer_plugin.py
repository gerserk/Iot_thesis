LATENCY= 5 # ascolta e manda ogni 5 secondi
USER='dhadmin'
PASSWORD='dhadmin_#911'
AUTH_URL='http://francesco-legion-5-15ach6h/api/rest'
URL='http://francesco-legion-5-15ach6h/plugin/proxy/'
BROKER = 'francesco-legion-5-15ach6h'
TOPIC_NAME='dh/request'
TOKEN= 'eyJhbGciOiJIUzI1NiJ9.eyJwYXlsb2FkIjp7ImEiOlsxNl0sImUiOjE2ODIzNTQwMDk4MTksInQiOjEsInRwYyI6InBsdWdpbl90b3BpY19kZjEwYWI2OC04NjYyLTQ0ODItYWFjNC1jMzI3NWI4YTMzNGMifX0.gEzo-ZdfpfiG2cg7sN-A9jeEp84OHAAtlLip5wr98_s'

import paho.mqtt.client as mqtt
import uuid
import json
import time
from devicehive_plugin import Handler
from devicehive_plugin import Plugin


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
        print(notification.notification)

plugin = Plugin(SimpleHandler)
#plugin.connect(URL, TOPIC_NAME, auth_url=AUTH_URL, login=USER, password=PASSWORD) 
plugin.connect(URL, TOPIC_NAME, plugin_access_token=TOKEN)