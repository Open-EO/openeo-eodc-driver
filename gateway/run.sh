#!/bin/sh

until nc -z ${RABBIT_HOST} ${RABBIT_PORT}; do
    echo "$(date) - waiting for rabbitmq..."
    sleep 1
done

echo "$(date) - Started gateway"
gunicorn -c /usr/src/app/gunicorncfg.py wsgi:app
