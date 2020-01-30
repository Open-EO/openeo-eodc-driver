#!/bin/sh

until nc -z ${RABBIT_HOST} ${RABBIT_PORT}; do
    echo "$(date) - waiting for rabbitmq..."
    sleep 1
done

echo "$(date) - Started gateway"
python3 manage.py prod -b $HOST:$GATEWAY_PORT -w $NO_WORKERS -t $TIMEOUT
