#!/bin/bash

docker cp setup_scripts/sample-auth.sh oeo-users-v1.0:/usr/src/app/sample-auth.sh
docker cp setup_scripts/add_init_users.py oeo-users-v1.0:/usr/src/app/add_init_users.py

docker exec oeo-users-v1.0 source /usr/src/app/sample-auth.sh
docker exec oeo-users-v1.0 python /usr/src/app/add_init_users.py

docker exec oeo-users-v1.0 rm /usr/src/app/add_init_users.py
docker exec oeo-users-v1.0 rm /usr/src/app/sample-auth.sh
