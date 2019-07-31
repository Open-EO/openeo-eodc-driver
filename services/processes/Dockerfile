FROM openeo-base
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
RUN mkdir /usr/src/api
RUN chown www-openeo:openeo /usr/src/api
USER www-openeo
CMD nameko run --config config.yaml processes.service --backdoor 3000
