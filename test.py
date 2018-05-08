from requests import get
from json import loads
from urllib.parse import quote

class MetricsWatcher:
    def __init__(self, namespace_name):
        self.hawkular_api = "https://metrics.193.170.203.100.xip.io/hawkular/metrics"
        self.auth = "Bearer zh-aoIqX67R9m8Y9gASpl9ySAvFNrMQI7ZNKMSnICak"
        self.verify = False
        self.namespace_name = namespace_name
        self.timestamps = {}
        self.data = {}

    def send_request(self, path):
        response = get(self.hawkular_api  + path, 
                       headers={
                           "Authorization": self.auth, 
                           "Hawkular-Tenant": self.namespace_name}, 
                       verify=self.verify)

        response.raise_for_status()
        return loads(response.text)

    def update_metrics(self, pod_name, start):
        self.timestamps[pod_name] = start

        path = "/metrics?tags=labels.name:" + pod_name
        metrics = self.send_request(path)

        for metric in metrics:
            m_path = "/{0}s/{1}/data?start={2}".format(metric["type"], quote(metric["id"], safe=''), start)
            m_data = self.send_request(m_path)

            m_name = metric["tags"]["descriptor_name"]
            if m_name not in self.data:
                self.data[m_name] = m_data
            else:
                self.data[m_name] += m_data
    


namespace_name = "openeo"

metrics_watcher = MetricsWatcher(namespace_name)

pod_name = "openeo-data" 
start = "1521548437000"
metrics_watcher.update_metrics(pod_name, start)

pod_name = "openeo-data" 
start = "1521549037000"
metrics_watcher.update_metrics(pod_name, start)

stop = 1

# {
#         "id": "pod/9f198986-23a0-11e8-a75b-fa163e831d64/network/rx_errors_rate",
#         "tags": {
#             "descriptor_name": "network/rx_errors_rate",
#             "group_id": "/network/rx_errors_rate",
#             "host_id": "10.250.17.148",
#             "hostname": "10.250.17.148",
#             "labels": "deployment:openeo-data-12,deploymentconfig:openeo-data,name:openeo-data",
#             "labels.deployment": "openeo-data-12",
#             "labels.deploymentconfig": "openeo-data",
#             "labels.name": "openeo-data",
#             "namespace_id": "4167732f-1ba9-11e8-a75b-fa163e831d64",
#             "namespace_name": "openeo",
#             "nodename": "10.250.17.148",
#             "pod_id": "9f198986-23a0-11e8-a75b-fa163e831d64",
#             "pod_name": "openeo-data-12-57jp5",
#             "pod_namespace": "openeo",
#             "type": "pod"
#         },
#         "dataRetention": 7,
#         "type": "gauge",
#         "tenantId": "openeo:4167732f-1ba9-11e8-a75b-fa163e831d64"
#     },


#     def get_uptime(self, ):
#         https://metrics.193.170.203.100.xip.io/hawkular/metrics/counters/openeo-data%2F9f198986-23a0-11e8-a75b-fa163e831d64%2Fuptime/data?start=1521547551000


#     def get_cpu_usage(self, ):
#         https://metrics.193.170.203.100.xip.io/hawkular/metrics/counters/openeo-data%2F9f198986-23a0-11e8-a75b-fa163e831d64%2Fcpu%2Fusage/data?start=1521547551000
    
#     def get_cpu_limit(self, ):
#         https://metrics.193.170.203.100.xip.io/hawkular/metrics/gauges/openeo-data%2F9f198986-23a0-11e8-a75b-fa163e831d64%2Fcpu%2Flimit/data?start=1521547551000
    
#     def get_cpu_request(self, ):
#         https://metrics.193.170.203.100.xip.io/hawkular/metrics/gauges/openeo-data%2F9f198986-23a0-11e8-a75b-fa163e831d64%2Fcpu%2Frequest/data?start=1521547551000
    

#     def get_memory_usage(self, ):
#         https://metrics.193.170.203.100.xip.io/hawkular/metrics/gauges/openeo-data%2F9f198986-23a0-11e8-a75b-fa163e831d64%2Fmemory%2Fusage/data?start=1521547551000
    
#     def get_memory_limit(self, ):
#         https://metrics.193.170.203.100.xip.io/hawkular/metrics/gauges/openeo-data%2F9f198986-23a0-11e8-a75b-fa163e831d64%2Fmemory%2Flimit/data?start=1521547551000

#     def get_memory_request(self, ):
#         https://metrics.193.170.203.100.xip.io/hawkular/metrics/gauges/openeo-data%2F9f198986-23a0-11e8-a75b-fa163e831d64%2Fmemory%2Frequest/data?start=1521547551000


# def get_memory_usage(self, ):
#         https://metrics.193.170.203.100.xip.io/hawkular/metrics/gauges/openeo-data%2F9f198986-23a0-11e8-a75b-fa163e831d64%2Fmemory%2Fusage/data?start=1521547551000
    
#     def get_memory_limit(self, ):
#         https://metrics.193.170.203.100.xip.io/hawkular/metrics/gauges/openeo-data%2F9f198986-23a0-11e8-a75b-fa163e831d64%2Fmemory%2Flimit/data?start=1521547551000

#     def get_memory_request(self, ):
#         https://metrics.193.170.203.100.xip.io/hawkular/metrics/gauges/openeo-data%2F9f198986-23a0-11e8-a75b-fa163e831d64%2Fmemory%2Frequest/data?start=1521547551000





#     def get_pod_metrics_data(self):






# def get_pod_metric_ids(project, pod_name):
    
    
#     return result

# def get_pod_metrics_data(pod_metric_ids):

#     data = []   
#     for pod_metric in pod_metric_ids:
#         url = "{0}/metrics?tags=labels.name:{1}".format(HAWKULAR_API, pod_name)

#     metric_ids = []
#     for metric in result:





# https://metrics.193.170.203.100.xip.io/hawkular/metrics/metrics?tags=labels.name:openeo-process





# project = "openeo"
# path = "metrics"
# container = "openeo-user%2Ffb5ce920-237f-11e8-a75b-fa163e831d64"
# metric_1 = "cpu"
# metric_2 = "usage"

# url = "{0}/{1}/{2}".format(hawkular_api, path, container)

# response = get(url, headers={"Authorization": auth, "Hawkular-Tenant": project}, verify=False)
# response.raise_for_status()

# result = 
# stop = 1


# # uptime

# # memory/usage
# # memory/request
# # memory/limit

# # cpu/usage
# # cpu/request
# # cpu/limit

# # disk/io_read_bytes
# # disk/io_write_bytes