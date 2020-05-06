FROM puckel/docker-airflow:1.10.9
ENV FLASK_ENV='production'
USER root

# Get GDAL dependencies for eoDataReaders
RUN echo "deb http://http.us.debian.org/debian bullseye main non-free contrib" >> /etc/apt/sources.list && \
    echo "deb-src http://http.us.debian.org/debian bullseye main non-free contrib" >> /etc/apt/sources.list
RUN apt-get update -y
RUN apt-get install -y gdal-bin libgdal-dev git ssh && apt-get install -f
RUN pip install --upgrade pip # uncomment when this issue is fixed: https://github.com/pypa/pip/issues/7217
RUN pip install GDAL==$(gdal-config --version) --global-option=build_ext --global-option="-I/usr/include/gdal"
# Fix pandas version must be >=0.25 and <1.0.0
RUN pip uninstall -y pandas && pip install pandas==0.25
# Install eoDataReaders
RUN mkdir /root/.ssh
COPY deploy.key /root/.ssh/id_rsa
RUN touch /root/.ssh/known_hosts
RUN chmod 600 /root/.ssh/id_rsa
RUN ssh-keyscan git.eodc.eu >> /root/.ssh/known_hosts
WORKDIR /tmp
RUN git clone git+ssh://git@git.eodc.eu/eodc/eoDataReaders.git
WORKDIR /tmp/eoDataReaders
RUN git checkout tags/v1.0.2
RUN /bin/bash -c "python3 setup.py install"

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
