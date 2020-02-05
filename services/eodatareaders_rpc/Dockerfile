FROM openeo-eodc-airflow
USER root
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt .
COPY run.sh .
RUN python3 -m pip install -r requirements.txt 
RUN pip install numpy==1.16.1
USER airflow
CMD ["./run.sh"]
