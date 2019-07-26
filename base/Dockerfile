FROM python:3.6-alpine
RUN addgroup -S openeo && adduser -S www-openeo -G openeo
RUN apk update && \
    apk add build-base libressl-dev libffi-dev gcc python3-dev musl-dev postgresql-dev git && \
    pip3 install --upgrade pip
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
