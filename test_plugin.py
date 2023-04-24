from devicehive_plugin import Handler
from devicehive_plugin import Plugin


class SimpleHandler(Handler):

    def handle_connect(self):
        print('Successfully connected')

    def handle_event(self, event):
        print(event.action)
        print(type(event.data))

    def handle_command_insert(self, command):
        print(command.command)

    def handle_command_update(self, command):
        print(command.command)

    def handle_notification(self, notification):
        print(notification.notification)

url = 'ws://francesco-legion-5-15ach6h/plugin/proxy/'
topic_name = 'PLUGIN_TOPIC' #REPLACE PLUGIN TOPIC HERE
plugin_access_token = 'PLUGIN_ACCESS_TOKEN' #REPLACE PLUGIN ACCESS TOKEN HERE
plugin = Plugin(SimpleHandler)
plugin.connect(url, topic_name, plugin_access_token=plugin_access_token)