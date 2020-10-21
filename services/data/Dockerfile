ARG OPENEO_VERSION
FROM oeo-base-$OPENEO_VERSION
COPY requirements.txt .
COPY run.sh .
COPY config.yaml .
RUN python3 -m pip install -r requirements.txt
COPY data ./data
RUN mkdir /usr/src/cache
RUN chown www-openeo:airflow /usr/src/cache
USER www-openeo
CMD ["./run.sh"]
