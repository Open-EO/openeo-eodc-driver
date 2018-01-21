import requests
import json
import yaml
from config import server_ip, token, namespace
from template_a import template


ahhhhh = {
    "apiVersion": "v1",
    "kind": "ImageStream",
    "metadata": {
        "name": "nodejs-rest-http"
    },
    "spec": {}
}

url = server_ip + "/oapi/v1/namespaces/myproject/imagestreams"
headers = {"Authorization": "Bearer " + token}

response = requests.post(url, data=json.dumps(ahhhhh), headers=headers, verify=False)

print(response.text)