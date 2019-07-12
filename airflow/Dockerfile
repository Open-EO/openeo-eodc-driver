FROM puckel/docker-airflow:latest 
USER root
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
RUN git clone -b remove-eomDR git+ssh://git@git.eodc.eu/eodc/eoDataReaders.git
WORKDIR /tmp/eoDataReaders
#Temporary hack
RUN git checkout f19a1c66
RUN /bin/bash -c "python3 setup.py install"
RUN apt-get autoremove -y && \
  rm -rf /var/lib/apt/lists/*
USER airflow