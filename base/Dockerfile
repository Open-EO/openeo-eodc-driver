FROM python:3.6.11
# Add use rwith gid 1000 (important), gid also 1000 to be sure
ENV USER=www-openeo
ENV UID=1000
ENV GROUP=airflow
ENV GID=1000
RUN addgroup --gid "$GID" "$GROUP" \
    && adduser \
    --disabled-password \
    --gecos "" \
    --ingroup "$GROUP" \
    --uid "$UID" \
    "$USER"
RUN apt-get update && apt-get install netcat -y && pip3 install --upgrade pip
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
# Needed by gateway and services files and jobs
RUN mkdir /usr/src/files/
RUN chown www-openeo:airflow /usr/src/files
