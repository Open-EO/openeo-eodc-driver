# VERSION 1.10.2
# AUTHOR: Matthieu "Puckel_" Roisil
# DESCRIPTION: Basic Airflow container
# BUILD: docker build --rm -t puckel/docker-airflow .
# SOURCE: https://github.com/puckel/docker-airflow

# LABEL maintainer="Puckel_"
# This Dockerfile was modified from the one created by Matthieu "Puckel_" Roisil
FROM osgeo/gdal:ubuntu-small-latest

# Never prompts the user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux

# Airflow
#ARG AIRFLOW_VERSION=1.10.2 -> this version does not work
ARG AIRFLOW_VERSION=1.10.1
ARG AIRFLOW_HOME=/usr/local/airflow
ARG AIRFLOW_DEPS=""
ARG PYTHON_DEPS=""
ENV AIRFLOW_GPL_UNIDECODE yes

# Define en_US.
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8

RUN set -ex \
    && buildDeps=' \
        freetds-dev \
        libkrb5-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        libpq-dev \
    ' \
    && apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq python3-pip \
    && apt-get install -yqq --no-install-recommends \
        $buildDeps \
        freetds-bin \
        build-essential \
        default-libmysqlclient-dev \
        apt-utils \
        curl \
        rsync \
        netcat \
        locales \
        git \
        openssh-client \
        wget \
    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && useradd -ms /bin/bash -d ${AIRFLOW_HOME} airflow \
    && pip3 install -U setuptools wheel \
    && pip3 install pytz \
    && pip3 install pyOpenSSL \
    && pip3 install ndg-httpsclient \
    && pip3 install pyasn1 \
    && pip3 install apache-airflow[crypto,celery,postgres,hive,jdbc,mysql,ssh${AIRFLOW_DEPS:+,}${AIRFLOW_DEPS}]==${AIRFLOW_VERSION} \
    #&& pip3 install 'redis>=2.10.5,<3' \
    && pip3 install 'redis>=3.2.0' \
    && if [ -n "${PYTHON_DEPS}" ]; then pip3 install ${PYTHON_DEPS}; fi \
    && apt-get purge --auto-remove -yqq $buildDeps \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

COPY script/entrypoint.sh /entrypoint.sh
COPY config/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg
COPY requirements.txt /requirements.txt

## Install eoDataReaders package
# Add deploy key
ARG SSH_PRIVATE_KEY
RUN mkdir /root/.ssh/
ADD ./deploy-key /root/.ssh/id_rsa
RUN chmod 0600 /root/.ssh/id_rsa

# Make sure the EODC gitlab is accepted
RUN touch /root/.ssh/known_hosts
RUN ssh-keyscan git.eodc.eu >> /root/.ssh/known_hosts

# Get eoDataReaders
WORKDIR /tmp
RUN git clone -b eodc-forum git+ssh://git@git.eodc.eu/eodc/eoDataReaders.git
WORKDIR /tmp/eoDataReaders
RUN git checkout f19a1c66
# Install eoDataReaders libary
WORKDIR /tmp/eoDataReaders
RUN /bin/bash -c "python3 setup.py install"

RUN chown -R airflow: ${AIRFLOW_HOME}

EXPOSE 8080 5555 8793

USER airflow
WORKDIR ${AIRFLOW_HOME}
ENTRYPOINT ["/entrypoint.sh"]
CMD ["webserver"] # set default arg for entrypoint
