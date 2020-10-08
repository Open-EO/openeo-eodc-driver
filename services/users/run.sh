#!/bin/sh
set -x

until nc -z ${OEO_RABBIT_HOST} ${OEO_RABBIT_PORT}; do
    ping -c 1 ${OEO_RABBIT_HOST}

    echo "$(date) - waiting for rabbitmq..."
    sleep 1
done

echo "$(date) - Started users.service"
nameko run --config config.yaml users.service --backdoor 3000
