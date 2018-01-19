import requests
import json

deployconfig = {
    "kind": "Deployment",
    "apiVersion": "apps/v1beta1",
    "metadata": {
        "name": "my-project-deployment"
    },
    "spec": {
        "replicas": 1,
        "template": {
            "metadata": {
                "labels": {"label1": "test1234"}
            },
            "spec": {
                "containers": [
                    {
                        "name": "my-project-ruby-test",
                        "image": "mysql"
                    }
                ]
            }
        }
    }
}

url = "https://192.168.137.108:8443/apis/apps/v1beta1/namespaces/myproject/deployments"
token = "PVeInZZF1Z3Enk2nPHLEcimsEgG-UJxTr-8vz0q-ZGE"
headers = {"Authorization": "Bearer " + token}

response = requests.post(url, data=json.dumps(deployconfig), headers=headers, verify=False)

print(response.headers['content-type'])
print(response.text)
