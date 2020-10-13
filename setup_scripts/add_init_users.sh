#!/bin/bash

docker cp setup_scripts/add_init_users.py oeo-users-v1.0:/usr/src/app/add_init_users.py
docker exec \
  -e USER_BASIC_ADMIN="my-username" \
  -e PASSWORD_BASIC_ADMIN="my-password" \
  -e EMAIL_OIDC_ADMIN="my-name@sample.com" \
  -e PROFILE_1_NAME="profile_1" \
  -e PROFILE_1_DATA_ACCESS="basic,pro" \
  -e PROFILE_2_NAME="profile_2" \
  -e PROFILE_2_DATA_ACCESS="basic" \
  -e ID_PROVIDER_ID="google" \
  -e ID_PROVIDER_ISSUER_URL="https://accounts.google.com" \
  -e ID_PROVIDER_TITLE="Google" \
  -e ID_PROVIDER_DESCRIPTION="Identity Provider supported in this back-end." \
  oeo-users-v1.0 /bin/bash -c 'python /usr/src/app/add_init_users.py'
