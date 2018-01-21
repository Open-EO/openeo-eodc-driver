import requests
import json

buildconfig = {
    "apiVersion": "build.openshift.io/v1",
    "kind": "BuildConfig",
    "metadata": {
        "annotations": {
            "generated-by": "EODC_Benchmark"
        },
        "labels": {
            "app": "ruby-hello-world"
        },
        "name": "ruby-hello-world",
        "namespace": "myproject"
    },
    "spec": {
        "failedBuildsHistoryLimit": 5,
        "successfulBuildsHistoryLimit": 5,
        "source": { 
            "type": "Git",
            "git": {
                "uri": "https://github.com/openshift/ruby-hello-world",
            }
        },
        "strategy": {
            "type": "Docker",
            "dockerStrategy": {
                "from": {
                    "kind": "DockerImage",
                    "name": "ruby-20-centos7:latest"
                }
            }
        },
        "output": {
            "to": {
                "kind": "ImageStreamTag",
                "name": "ruby-hello-world:latest"
            }
        },
        "runPolicy": "Serial"
    }
}

url = "https://192.168.137.166:8443/apis/build.openshift.io/v1/namespaces/myproject/buildconfigs"
token = "gfnBhc6LiQVN2czGoUKCva2vtAwUEiO18DK4wjxgNQw"
headers = {"Authorization": "Bearer " + token}

response = requests.post(url, data=json.dumps(buildconfig), headers=headers, verify=False)

print(response.headers['content-type'])
print(response.text)
