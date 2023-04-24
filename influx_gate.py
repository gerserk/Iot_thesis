API_TOKEN='SkmJM1EVrXzLmZLE6K1RntVWg8AHaPsSYAbgRR74BOxN1Rlrm9NeXK5K78HdmHb41jx68RmlmSPP8DJVX6bIHg=='
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import json
from dateutil import parser
import random
import datetime 
token = API_TOKEN
org = "aquaseek"
url = "http://francesco-legion-5-15ach6h:8086"
bucket='machine_a'

class TemperatureSensor(object):
    def rand(self):
        return round(-0.25 + 0.5 * random.random(), 2)

    def get_temp(self):
        return 25 + self.rand()

while True:
    a=TemperatureSensor()
    temperature=a.get_temp()

    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    point=Point('measurement').tag('sensor_name','DHT_001').field('temperature',temperature)

#data={"time":time.ctime(),'name':'prova','action':'notification','temperature':0000}#here in reality arruves as message
    write_api.write(bucket=bucket, org=org, record=point)
    time.sleep(10)

# point= measurement tag-metadata field=actual values timestamp

