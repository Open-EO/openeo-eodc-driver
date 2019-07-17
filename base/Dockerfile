FROM python:3.6-alpine
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt .
RUN apk update && \
    apk add build-base libressl-dev libffi-dev gcc python3-dev musl-dev postgresql-dev git && \
    pip3 install --upgrade pip
RUN python3 -m pip install -r requirements.txt
