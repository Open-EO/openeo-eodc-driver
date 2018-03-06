from __future__ import absolute_import, unicode_literals
from os import environ
from celery import Celery

broker = "amqp://{user}:{password}@{host}:5672//"
broker = broker.format(user=environ.get("RABBIT_MQ_USER"), 
                        password=environ.get("RABBIT_MQ_PASSWORD"), 
                        host=environ.get("RABBIT_MQ_HOST"))

app = Celery("openeo_tasks", 
             broker=broker, 
             include=['src.tasks'])

if __name__ == '__main__':
    app.start()