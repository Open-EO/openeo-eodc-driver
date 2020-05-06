ARG OPENEO_VERSION
FROM oeo-base-$OPENEO_VERSION
COPY requirements.txt .
COPY run.sh .
RUN python3 -m pip install -r requirements.txt
RUN mkdir /usr/src/api
RUN chown www-openeo:airflow /usr/src/api
USER www-openeo
#CMD alembic upgrade head
CMD ["./run.sh"]
