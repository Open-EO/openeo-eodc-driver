import requests
import json
from config import server_ip, token, namespace

build = {
    "kind": "Build",
    "apiVersion": "build.openshift.io/v1",
    "metadata": {
        "name": "myproject-build",
        "namespace": namespace
    },
    "spec": {
        "source": {
            "type": "Git",
            "git": {
                "uri": "https://github.com/openshift/ruby-hello-world",
            }
        },
        "strategy": {
            "type": "Docker",
            "dockerStrategy": {
                "dockerfilePath": "Dockerfile",
                "name": "ruby-20-centos7:latest"
            }
        },
         "output": {
            "to": {
                "kind": "DockerImage",
                "name": "myproject-build:latest",
                "namespace": namespace
            }
        }
    }
}

url = server_ip + "/apis/build.openshift.io/v1/namespaces/" + namespace + "/builds"
headers = {"Authorization": "Bearer " + token}

response = requests.post(url, data=json.dumps(build), headers=headers, verify=False)

print(response.headers['content-type'])
print(response.text)
