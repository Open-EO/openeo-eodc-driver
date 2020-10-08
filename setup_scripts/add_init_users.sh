docker cp setup_scripts/add_init_users.py oeo-users-v1.0:/usr/src
docker exec -it oeo-users-v1.0 bash
python /usr/src/add_init_users.py
rm /usr/src/add_init_users.py
