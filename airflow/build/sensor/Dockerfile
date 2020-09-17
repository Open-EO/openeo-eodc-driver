FROM puckel/docker-airflow:1.10.9
ENV FLASK_ENV='production'
USER root

RUN apt-get update -y
RUN apt-get install -y git

# Install gevent for sensor worker pool
RUN pip install gevent

# WARNING: this is a dirty monkey patch!!!
# There is currently an open PR on this in Airflow
# https://github.com/apache/airflow/issues/8023
# should be removed once patch is upstream
# created with Aitflow 1.10.9 may NOT work with ANY other version!!!
# Gevent pool Monkey patch start
WORKDIR /usr/local/lib/python3.7/site-packages/airflow
COPY ./gevent_pool.patch .
RUN git init
RUN git apply gevent_pool.patch
RUN rm gevent_pool.patch
# Gevent pool Monkey patch end

RUN mkdir /usr/local/airflow/logs
RUN apt-get autoremove -y && \
  rm -rf /var/lib/apt/lists/*
RUN chown -R airflow: /usr/local/airflow
USER airflow
WORKDIR /usr/local/airflow
