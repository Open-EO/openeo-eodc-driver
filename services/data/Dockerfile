FROM openeo-base
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
RUN mkdir /usr/src/cache
RUN chown www-openeo:airflow /usr/src/cache
USER www-openeo
CMD nameko run --config config.yaml data.service
