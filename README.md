# openEO EODC Driver

## Information

- version: 0.4

## NGINX Proxy and Letsencrypt Setup

This setup uses an NGINX Proxy in combination with Docker Gen and LetsEncrypt to auto create and renew SSL certificates for https.

- NGINX Proxy Docker image: https://github.com/jwilder/nginx-proxy
- Letsencrypt NGINX Docker Companion: https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion

Copy `sample.env` to `.env` and adjust the environment variables. These variables are needed for the NGINX proxy and LetsEncrypt NGINX Proxy Companion to work.
Do not add `.env`to a git repository! (added to `.gitgnore` by default - don't change this!)

```bash
VIRTUAL_HOST=example.com # Your domain
VIRTUAL_PORT=3000 # Gateway port. Default 3000
LETSENCRYPT_HOST= example.com # Your domain (has to be the same as VIRTUAL_HOST)
LETSENCRYPT_EMAIL=example@example.com
LETSENCRYPT_TEST='false' # set to true in development environment
PROJECT_NAME=openeo-openshift-driver # name this after project folder  
```

## Environment variables

Each container has its own environment file.

*Copy the `sample-envs` directory to `./envs`
*Adjust each environment file accordingly
*Make sure to use secure and unique credentials!
*Do not add `./envs`to a git repository! (added to `.gitgnore` by default - don't change this!)

## Persistent data

*NGINX config files and SSL certs are bind mounted to the host at `/srv/nginx/data/`.
*PostgreSQL databases are bind mounted to `/srv/openeo/data/jobs_db_data`and `/srv/openeo/data/processes_db_data`.

It is a good idea to mount a seperate logical volume to the `/srv` directory of the Docker host.

## MTU Settings in OpenStack

A common problem running docker in OpenStack and possibly other virtualization infrastructure is that the attached network interfaces do not have the default MTU of 1500.
In this case you have to change the default Docker MTU from 1500 to e.g. 1450

Should you be running docker on OpenStack follow these steps: 

*Use your editor of choice and edit `/etc/docker/daemon.json`
*If the file does not exist, create it.

```bash
sudo vim /etc/docker/daemon.json
```

*Paste the following lines.

```json
{
    "mtu": 1450
}
```

*Restart Docker

```bash
sudo systemctl restart docker
```

*Edit `docker-compose.nginx.yml` and uncomment the driver options.

```yml
networks:
  proxy:
    driver: bridge
#   Custom MTU overide needed for OpenStack environment only.
    driver_opts: 
        com.docker.network.driver.mtu: 1400
```

## Build and start the containers

To create the images and start the docker containers use the `run.sh` script.
The script will check if image dependencies are met, build necessary images and start the containers.

After the script completes succesfully it will create an empty `.init` file. This is needed in case
you want to use the `run.sh` script the image build process is skipped.

*Make the script executable and run it.

```bash
sudo chmod +x run.sh
./run.sh
```


































