from celery import Celery

app = Celery('worker',
             broker='redis://:pwd@localhost',
             backend='redis://:pwd@localhost',
             include=['worker.tasks'])

if __name__ == '__main__':
    app.start()
