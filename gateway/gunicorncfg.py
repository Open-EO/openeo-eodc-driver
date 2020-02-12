import os
import multiprocessing

bind = "{}:{}".format(
    os.environ.get("HOST", '0.0.0.0'),
    os.environ.get("GATEWAY_PORT", 3000))

NO_CORES = multiprocessing.cpu_count()
workers = os.environ.get("NO_WORKERS", NO_CORES * 2 + 1)
worker_class = os.environ.get("WORKER_CLASS", 'gthread')
timeout = os.environ.get("TIMEOUT", 360)

ACCESS_LOG_NAME = 'gateway_access.log'
ERROR_LOG_NAME = 'gateway_error.log'
LOG_PATH = os.environ.get("LOG_PATH", '/usr/src/logs')
accesslog = '{}/{}'.format(LOG_PATH, ACCESS_LOG_NAME)
errorlog = '{}/{}'.format(LOG_PATH, ERROR_LOG_NAME)
