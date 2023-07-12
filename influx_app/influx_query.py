import requests
import json
from fastapi import FastAPI,Request, HTTPException
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision, BucketsApi
from influxdb_client.client.flux_table import TableList
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


client = influxdb_client.InfluxDBClient(url=url_influx, username=influx_user, password=influx_password,org=org) 
write_api = client.write_api(write_options=SYNCHRONOUS)

bucket='machine-c'
timez='1'
misura_tempo='y' #s, m, h, d, y, se mette month metti 30 days
nome_field="temperature1"

query_api = client.query_api() 
query = f'from(bucket:"{bucket}")\
|> range(start: -{timez}{misura_tempo})\
|> filter(fn:(r) => r._field == "{nome_field}")' 

result = query_api.query(org=org, query=query)
results = []
for table in result:
    for record in table.records:
        results.append((record.get_field(), record.get_value()))
print(results)

