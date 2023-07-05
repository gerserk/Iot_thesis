import requests

a=requests.post("http://0.0.0.0:5000/info_bucket","machine-c")
print(a.content)