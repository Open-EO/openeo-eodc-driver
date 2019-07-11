FROM python:3.7-slim AS python-build
RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"
RUN apt-get update -y
RUN apt-get install -y gdal-bin git && apt-get install -f
RUN mkdir /root/.ssh
COPY deploy.key /root/.ssh/id_rsa
RUN touch /root/.ssh/known_hosts
RUN chmod 600 /root/.ssh/id_rsa
RUN ssh-keyscan git.eodc.eu >> /root/.ssh/known_hosts
WORKDIR /tmp
RUN git clone -b remove-eomDR git+ssh://git@git.eodc.eu/eodc/eoDataReaders.git
WORKDIR /tmp/eoDataReaders
RUN /bin/bash -c "python3 setup.py install"
RUN apt-get autoremove -y && \
  rm -rf /var/lib/apt/lists/*

FROM puckel/docker-airflow:latest AS airflow-eoDataReaders
COPY --from=python-build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"