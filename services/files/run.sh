#!/bin/sh

until nc -z ${RABBIT_HOST} ${RABBIT_PORT}; do
    echo "$(date) - waiting for rabbitmq..."
    sleep 1
done

echo "$(date) - Started files.service"
nameko run --config config.yaml files.service --backdoor 3000
