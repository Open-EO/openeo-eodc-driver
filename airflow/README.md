# Openeo EODC Apache Airflow Docker Image

## Edit Environment variables

Copy `sample.env` to `.env` and update the file as needed. This file is included in the `.gitignore` by default. Do not change this.

### Build the Docker Image

This docker image is based on: [puckel/docker-airflow](https://github.com/puckel/docker-airflow) and extends Apache Airflow with the GDAL environment and eoDataReaders. *Note: currently the `eoDataReaders` package is on a private repository. Therefore a deploy key is needed in order to build the image or else it will fail. This will change as soon as `eoDataReaders` will be open sourced (date tbd).*

Apache Airflow setting can be modified in `./build/airflow.cfg`. This has to be done before building the image. Respect to the basic setup, the `dag_dir_list_interval` is set to 1 second (instead of 5 minutes).

## Bring up Apache Airflow

```bash
docker-compose up -d
```
