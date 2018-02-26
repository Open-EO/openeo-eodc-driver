from celery import Celery

app = Celery('worker',
             broker='redis://:AqN6WqN3J2751xpV@localhost',
             backend='redis://:AqN6WqN3J2751xpV@localhost',
             include=['worker.tasks'])

if __name__ == '__main__':
    app.start()
