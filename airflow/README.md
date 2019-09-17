# Openeo EODC Airflow Docker Image

## Setup

### Build the Docker Image

This docker image is based on: [puckel/docker-ariflow](https://github.com/puckel/docker-airflow) and extends Airflow with
an GDAL environment.

Optionally modify Airflow settings in `./build/airflow.cfg`. This has to be done before building the image.

* *Currenty the `eoDataReaders` package is on a private repository needing a deploy key- the git pull while building the image will fail. This will change as soon as `eoDataReaders` will be publicly available.* *

To build the image run the `build.sh`script. You will have to make the script executable by using following command.

```bash
sudo chmod +x ./build.sh
```

Run the script: `./build.sh` and wait for the `openeo-eodc-airflow` image to build successfully.

## Edit Environment variables

Copy `sample.env` and rename it to `.env`

``` bash
cp sample.env .env
```

Set secure credentials for REDIS and Postgres and adjust the paths where input and output data should be stored on the Docker host. Be sure to never commit `.env`. It is in `.gitignore` by default.

## Start Airflow Docker Containers

```bash
docker-compose up -d
```
