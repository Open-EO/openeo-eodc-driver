# openEO EODC Driver

## Information

- version: 0.4

This repository contains a fully dockerized implementation of the openEO API (openeo.org), written in Python. The web app implementation is based on Flask, while openEO functionalities are implemented as micro-services with Nameko.

Additionally, three docker-compose files implement a CSW server for data access (/csw), an Apache Airflow workflow management platform coupled to a Celery cluster for data processing (/airflow), and UDF Services for the R and Python languages (/udf). The whole setup can be installed on a laptop to simplify development, but each service can run on independent (set of) machines.

## Start the API

In order to start the API web app and its micro-services, 


run the following docker compose from the main folder:

```
docker-compose up -d
```

This uses the `docker-compose.yml`.

### Set environment variables

Each container has its own environment file.

- Copy the `sample-envs` directory to `./envs`
- Adjust each environment file accordingly
- Make sure to use secure and unique credentials!
- Do not add `./envs`to a git repository! (added to `.gitgnore` by default - don't change this!)


## Build and start the containers

To create the images and start the docker containers use the `run.sh` script.
The script will check if image dependencies are met, build necessary images and start the containers.

After the script completes succesfully it will create an empty `.init` file. This is needed in case
you want to use the `run.sh` script the image build process is skipped.

- Make the script executable and run it.

```bash
sudo chmod +x run.sh
./run.sh
```
