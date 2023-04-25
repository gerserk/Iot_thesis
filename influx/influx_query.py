import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

bucket = "machine_a"
org = "aquaseek"
token = "8KXIVI3tJJW6nHz5bohZY4fyOKkLv74ABnj8DvTS0XB6oj9zSXehD9RCwGjQu7YKtgUMbeGbeowTSqL2MKhqEw=="
url="http://francesco-legion-5-15ach6h:8086"

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

# Query script
query_api = client.query_api() #removed field below, apparently can't put {bucket} 
query = 'from(bucket:"machine_a")\
|> range(start: -1h)\
|> filter(fn:(r) => r._measurement == "measurement")\
|> filter(fn:(r) => r._field == "temperature")'

# range can decide how much time i can decide to extract data

result = query_api.query(org=org, query=query)
results = []
for table in result:
    for record in table.records:
        results.append((record.get_field(), record.get_value()))
