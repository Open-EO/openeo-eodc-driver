#!/bin/sh

until nc -z ${OEO_RABBIT_HOST} ${OEO_RABBIT_PORT}; do
    echo "$(date) - waiting for rabbitmq..."
    sleep 1
done

echo "$(date) - Started capabilities.service"
nameko run --config config.yaml capabilities.service --backdoor 3000
