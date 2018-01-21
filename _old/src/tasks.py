''' Celery Tasks '''

import os
from celery import Celery

# celery = Celery("benchmark-service", broker=os.environ.get('REDIS_URL'))
print(os.environ.get('REDIS_URL'))

# @celery.task
# def perform_benchmarking(settings):
#     ''' Perform a single benchmarking job on the OpenShift environment '''

#     print(str(settings))
#     return 1
