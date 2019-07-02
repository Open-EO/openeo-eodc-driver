FROM alpine:3.7
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
RUN apk update && \
    apk add build-base libressl-dev libffi-dev gcc python3-dev musl-dev postgresql-dev && \
    pip3 install --upgrade pip