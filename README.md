# openEO EODC Driver

- version: 0.4.x

## Information

This repository contains a fully dockerized implementation of the openEO API (openeo.org), written in Python. The web app implementation is based on Flask, while openEO functionalities are implemented as micro-services with Nameko.

Additionally, three docker-compose files implement a CSW server for data access (`/csw`), an Apache Airflow workflow management platform coupled to a Celery cluster for data processing (`/airflow`), and UDF Services for the R and Python languages (`/udf`). The whole setup can be installed on a laptop to simplify development, but each service can run on independent (set of) machines.

## Start the API

In order to start the API web app and its micro-services, a simple docker-compose up is needed. However some environment variables must be set first.

#### Set environment variables

Copy the `sample.env` file and the `/sample-envs` folder to to `.env` and `/envs`, respectively. The latter are included in the `.gitignore` by default. Do not change this. Variables in the `.env`file are used in `docker-compose.yml` when bringing up the project, while variables in the individual env files in `/envs` are available within each respective container. The following is the list of files to updte:

- `.env`
- `envs/data.env`
- `envs/eodatareaders.env`: do not change the content in this env file
- `envs/gateway.env`
- `envs/jobs.env`
- `envs/oidc.env`
- `envs/processes.env`
- `envs/pycsw.env`
- `envs/rabbitmq.env`
- `envs/users.env`


#### Bring up web app and services

**Small caveat**: one service in the API docker-compose (eodatareaders_rpc) depends on the docker image in `/airflow/build`, so that one must be built first (see instructions [here](./airflow/README.md)). This will change as soon as possible.

Run the following docker compose from the main folder:

```
docker-compose up -d
```

which uses the `docker-compose.yml` file.

#### Bring down web app and services

Run the following docker compose from the main folder:

```
docker-compose down
```
