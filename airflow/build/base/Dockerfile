FROM puckel/docker-airflow:1.10.9
ENV FLASK_ENV='production'
USER root

RUN mkdir /usr/local/airflow/logs
RUN apt-get autoremove -y && \
  rm -rf /var/lib/apt/lists/*
RUN chown -R airflow: /usr/local/airflow
USER airflow
WORKDIR /usr/local/airflow
