FROM python:3.6.2

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ADD ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt
ADD . /usr/src/app

ENTRYPOINT celery -A celery tasks --concurrency=5 --loglevel=info