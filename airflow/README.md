# Openeo EODC Apache Airflow Docker Image

## Edit Environment variables

Copy `/airflow/sample.env` to `/airflow/.env` and update the file as needed. Note that you MUST create manually the folder specififed for 'LOG_DIR_AIRFLOW'. The `/airflow/.env` file is included in the `.gitignore`
by default. Do not change this.

### Build the Docker Image

This docker image is based on: [puckel/docker-airflow](https://github.com/puckel/docker-airflow) and extends Apache
Airflow with the GDAL environment and eoDataReaders. *Note: currently the `eoDataReaders` package is on a private
repository. Therefore a deploy key is needed in order to build the image or else it will fail. This will change as soon
as `eoDataReaders` will be open sourced (date tbd).*

Apache Airflow setting can be modified in `./build/airflow_process.cfg` and `./build/airflow_sensor.cfg`.
In the current setup two celery workers with their own queues are used. The main _processing_ worker and a _sensor_
worker which is required to cancel processing. The two workers use different pool types (`prefork` - cpu processes
vs `gevent` - threads on one cpu). As the celery pool can only be specified using the config in Airflow two different
config files are required.

Respect to the basic Airflow config the following was changed / should be changed:

  * `[core]` `max_active_runs_per_dag` is set to 1 (a single dag cannot run twice a the same time)
  * `[scheduler]` `dag_dir_list_interval` is set to 1 second (instead of 5 minutes).
  * `[celery]` `pool`: is set to `prefork` or `gevent` respectively
  * `[celery]` `worker_concurrency` is set to `16` by default. This should be adopted depending on the setup.
  It should be considered that the sensor's concurrency can be set to a quite high number (e.g. `500`) as in this case
  only threads and not cpu cores are user. Contrary the process's concurrency completely depends on the available
  compute power.

Ensure all changes to the config are done before starting the containers. The config is mounted in the docker-compose.

Additionally it should be mentioned that the two workers answer to different queues (`process` vs `sensor`). Those have
to be defined in the start up command. If you use the provided docker-compose this is already set properly.

## Bring up Apache Airflow

```bash
docker-compose up -d
```
