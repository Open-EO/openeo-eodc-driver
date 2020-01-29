FROM puckel/docker-airflow:latest
ENV FLASK_ENV='production'
USER root
COPY airflow.cfg /usr/local/airflow/airflow.cfg
RUN echo "deb http://http.us.debian.org/debian unstable main non-free contrib" >> /etc/apt/sources.list && \
    echo "deb-src http://http.us.debian.org/debian unstable main non-free contrib" >> /etc/apt/sources.list
RUN apt-get update -y
RUN apt-get install -y gdal-bin libgdal-dev git ssh && apt-get install -f
RUN pip install --upgrade pip
RUN pip install GDAL==$(gdal-config --version) --global-option=build_ext --global-option="-I/usr/include/gdal"
RUN mkdir /root/.ssh
COPY deploy.key /root/.ssh/id_rsa
RUN touch /root/.ssh/known_hosts
RUN chmod 600 /root/.ssh/id_rsa
RUN ssh-keyscan git.eodc.eu >> /root/.ssh/known_hosts
WORKDIR /tmp
## To be removed when geopathfinder uses pyScaffold 3.x and can be installed as a dependency of eoDataReaders
RUN git clone -b eodr_hotfix https://github.com/TUW-GEO/geopathfinder.git
WORKDIR /tmp/geopathfinder
RUN /bin/bash -c "python3 setup.py install"
WORKDIR /tmp
##
RUN git clone -b reduce-hack git+ssh://git@git.eodc.eu/eodc/eoDataReaders.git
WORKDIR /tmp/eoDataReaders
# RUN git checkout 2c3c838c7824fe8804b7633e35e5949ed149579a
RUN /bin/bash -c "python3 setup.py install"
RUN apt-get autoremove -y && \
  rm -rf /var/lib/apt/lists/*
RUN chown -R airflow: /usr/local/airflow
USER airflow
WORKDIR /usr/local/airflow
