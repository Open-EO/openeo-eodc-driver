FROM python:3.6.2

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install -r requirements.txt
ADD . /usr/src/app

CMD nameko run --config config.yaml data.service
