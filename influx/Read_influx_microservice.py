import requests
import uvicorn
import json
from fastapi import FastAPI,Request, HTTPException
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision, BucketsApi
from influxdb_client.client.write_api import SYNCHRONOUS

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

app = FastAPI()

with open("config.json", "r") as f:
    config = json.load(f)

# chiavi influx
influx_user=config["influx_credentials"]["user"]
influx_password=config["influx_credentials"]["password"]
org = config["org"]
url_influx = config["url_influx"]

# Functions
def findbucket_by_name(client,name):
    info_bucket=client.find_bucket_by_name(name)
    list=info_bucket.to_dict()
    return(list)

client = influxdb_client.InfluxDBClient(url=url_influx, username=influx_user, password=influx_password,org=org) 
write_api = client.write_api(write_options=SYNCHRONOUS)
Bclient = influxdb_client.BucketsApi(client)


@app.get("/ping")
def ping():
    return {"message": "influx data retrieval service is available!"}
    
@app.get("/api") # qui mi faccio passare i parametri da mettere nella query. Tipo di valore, tempo e ?
def read_item(request: Request):
    uri = request.url.path
    parameters = dict(request.query_params)
    print("URI:", uri)
    print("Parameters:", parameters)
    return {"URI": uri, "Parameters": parameters}

@app.get("/delete_bucket")
def read_item(request: Request):
    parameters = dict(request.query_params)
    bucket=parameters['bucket'] # nome del bucket (quindi macchina)

    bucket_data=findbucket_by_name(Bclient,bucket)

    if bucket_data is None:
        return('this bucket does not exist')
    else:
        bucket_id=bucket_data['id']
        Bclient.delete_bucket(bucket_id)
        return("bucket delteted successfully!")

@app.get("/info_all_buckets")
def read_item(request: Request):

    buckets = Bclient.find_buckets()
    if buckets is None:
        return("No buckets available")
    else:
        return(f"here are all infos about the buckets! {buckets}")

@app.get("/info_bucket")
def read_item(request: Request):

    parameters = dict(request.query_params)
    bucket=parameters['bucket'] 
    bucket_data=findbucket_by_name(Bclient,bucket)
    if bucket_data is None:
        return('this bucket does not exist')
    else:
        return("bucket data: {bucket_data}")

@app.get("/new_password") # DA TESTARE
def read_item(request: Request):

    parameters = dict(request.query_params)
    user=parameters['bucket']
    new_pass=parameters['password']
    Bclient.update_password(user,new_pass)
    return("Password updated!")

@app.get("/data_field")
def read_item(request: Request):

    parameters = dict(request.query_params)
    
    bucket=parameters['bucket']
    t=parameters['t']
    misura_tempo=parameters['time_measure'] # s, m, h, d, y, se mette month metti 30 days
    field=parameters['field']

    query_api = client.query_api() 
    query = f'from(bucket:"{bucket}")\
    |> range(start: -{t}{misura_tempo})\
    |> filter(fn:(r) => r._field == "{field}")' 

    result = query_api.query(org=org, query=query)
    results = []
    for table in result:
        for record in table.records:
            results.append((record.get_field(), record.get_value()))
    return(results)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8083)