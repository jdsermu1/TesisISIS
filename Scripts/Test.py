import requests

##
import urllib.request
import json

url_str = ""

with urllib.request.urlopen(url_str) as url:
    data = json.loads(url.read().decode())
    print(data)
