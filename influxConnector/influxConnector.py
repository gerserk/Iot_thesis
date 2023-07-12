import uvicorn
import json
from fastapi import FastAPI,Request, HTTPException
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision, BucketsApi
from influxdb_client.client.write_api import SYNCHRONOUS
from devicehive import Handler
from devicehive_plugin import Plugin
import asyncio

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

# BUCKET KEYS
measures=config["bucket_keys"]["measurement"]
sens_name=config["bucket_keys"]["sensor_name"]

# Functions
def findbucket_by_name(client,name):
    info_bucket=client.find_bucket_by_name(name)
    list=info_bucket.to_dict()
    return(list)

client = influxdb_client.InfluxDBClient(url=url_influx, username=influx_user, password=influx_password,org=org) 
write_api = client.write_api(write_options=SYNCHRONOUS)
Bclient = influxdb_client.BucketsApi(client)

############# LIST ###################

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

        device_id= notification.device_id
        
        verifica=notification.parameters #= dict{'humidity': 30, 'temperature1': 25.15, 'temperature2': 25.03}
        
        if self.n==1:  # if the action is to insert a notification
            parameter=notification.parameters
            for measurment in parameter.keys(): # here i call every type of measure in the dictionary

                value=parameter[measurment] # nuova misura si registra in automatico

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
async def plugin_connect():
    plugin = Plugin(SimpleHandler)
    plugin.connect(url, topic_name, auth_url=auth_url,
                login=dh_credentials["user"], password=dh_credentials["password"])


############# APP ###################

# http://localhost:5000/ping
@app.get("/ping")
def ping():
    return {"message": "pong"}
    
@app.get("/api") # solo per prova
def read_item(request: Request):
    uri = request.url.path
    parameters = dict(request.query_params)
    print("URI:", uri)
    print("Parameters:", parameters)
    return {"URI": uri, "Parameters": parameters}

# http://localhost:5000/delete_bucket?bucket=machine_a
@app.get("/delete_bucket")
def read_item(request: Request):
    parameters = dict(request.query_params)
    bucket=parameters['bucket'] # nome del bucket (quindi macchina)

    buckets = Bclient.find_buckets()
    
    check=False
    
    list= buckets.buckets
    for i in range(len(list)):
        pagina=list[i]
        nome=pagina._name
        if nome==bucket:
            check=True
    
    if check is False:
        return({'message':'this bucket does not exist'})
    else:
        bucket_data=findbucket_by_name(Bclient,bucket)
        bucket_id=bucket_data['id']
        Bclient.delete_bucket(bucket_id)
        return({'message':'bucket delteted successfully!'})

# http://localhost:5000/info_all_buckets
@app.get("/info_all_buckets")
def read_item(request: Request):

    buckets = Bclient.find_buckets()
    if buckets is None:
        return("No buckets available")
    else:
        return buckets

# http://localhost:5000/info_bucket?bucket=machine_a
@app.post("/info_bucket")
async def read_item(request: Request):

    #bucket = await request.json()
    bucket = await request.body()
    bucket = bucket.decode()
    return {"value": bucket}
    # bucket_data=findbucket_by_name(Bclient,bucket)
    # if bucket_data is None:
    #     return('this bucket does not exist')
    # else:
    #     return bucket_data

# http://localhost:5000/data_field?bucket=machine_b&t=1&time_measure=y&field=temperature
@app.post("/read_data_field")

def read_item(request: Request):

    parameters = dict(request.query_params)
    body=request.body()
    bucket=parameters['bucket']
    t=parameters['t']
    misura_tempo=parameters['time_measure'] # s, m, h, d, y, se mette month metti 30 days
    field=parameters['field']

    if misura_tempo=='mh':
        t=int(t)
        t=30*t
        misura_tempo='d'

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

@app.post("/write_data_field")

def write_item(request: Request):

    parameters = dict(request.query_params)
    body=request.body()
    device_id=parameters['bucket']
    t=time.time_ns()
    measurment=parameters['measurment']
    value=parameters['value']

    point=Point
   
    point=Point(measures).tag(sens_name,device_id).field(measurment,value)
    write_api.write(bucket=device_id, org=org, record=point)

if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=5000)
    a=plugin_connect()
    asyncio.run(a)
    
    