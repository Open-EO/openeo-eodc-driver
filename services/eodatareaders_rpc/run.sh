#!/bin/sh

until nc -z ${RABBIT_HOST} ${RABBIT_PORT}; do
    echo "$(date) - waiting for rabbitmq..."
    sleep 1
done

echo "$(date) - Started eodatareaders_rpc.service"
nameko run --config config.yaml eodatareaders_rpc.service --backdoor 3000
