#!/bin/sh

until nc -z ${OEO_RABBIT_HOST} ${OEO_RABBIT_PORT}; do
    echo "$(date) - waiting for rabbitmq..."
    sleep 1
done

echo "$(date) - Started processes.service"
nameko run --config config.yaml processes.service --backdoor 3000
