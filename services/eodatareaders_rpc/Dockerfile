FROM openeo-eodc-airflow
USER root
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt 
USER airflow
CMD nameko run --config config.yaml eodatareaders_rpc.service --backdoor 3000
