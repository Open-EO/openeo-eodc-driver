FROM openeo-base
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
RUN mkdir /usr/src/files
RUN chown www-openeo:airflow /usr/src/files
USER www-openeo
CMD nameko run --config config.yaml files.service --backdoor 3000
