docker cp setup_scripts/add_init_users.py oeo-users-v1.0:/usr/src/app/add_init_users.py
docker exec -it oeo-users-v1.0 python /usr/src/app/add_init_users.py
docker exec -it oeo-users-v1.0 rm /usr/src/app/add_init_users.py
