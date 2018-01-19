import time
import openshift.client
from kubernetes.client.rest import ApiException
from pprint import pprint


# Configure API key authorization: BearerToken
openshift.client.configuration.api_key['authorization'] = 'nPWq1dqmtBW6cs_jDpUJQcpIhKrBQ2CRS9lgxEl_cYw'
api_instance = openshift.client.OapiApi()

namespace = "myproject"
body = """
kind: Template
apiVersion: v1
metadata:
  name: launchpad-builder1233
  annotations:
    description: This template creates a Build Configuration using an S2I builder.
    tags: instant-app
objects:
- apiVersion: v1
  kind: ImageStream
  metadata:
    name: nodejs-rest-http
  spec: {}
- apiVersion: v1
  kind: ImageStream
  metadata:
    labels:
      app: launchpad-builder3
    name: nodejs-rest-http
name: nodejs-rest-http
"""

try: 
    api_response = api_instance.create_namespaced_processed_template(namespace, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling OapiApi->create_namespaced_processed_template: %s\n" % e)