#!/bin/bash

check_container () {
  echo "### Checking if container ${1} exists. ###"
  if [ ! "$(docker ps -q -f name=${1})" ]; then
    echo "Container ${1} exists."
    echo "Checking container ${1} status"
      if [ "$(docker ps -aq -f status=exited -f name=${1})" ]; then
        echo "Container ${1} exited. Starting container"
        docker run ${1}
      fi
  fi
} 

# Init users database
check_container openeo-gateway && docker exec openeo-gateway /bin/sh -c "cd gateway/users; alembic upgrade head" && echo "### Done. ###"

# Init process graphs database
check_container openeo-processes && docker exec openeo-processes alembic upgrade head && echo "### Done. ###"

# Init job database
check_container openeo-jobs && docker exec openeo-jobs alembic upgrade head && echo "### Done. ###"
