#FROM python:3.6-alpine
FROM python:3.6
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
# RUN apk update && \
#     apk add --no-cache build-base libressl-dev libffi-dev gcc python3-dev musl-dev postgresql-dev git vim nano bash&& \
#     pip3 install --upgrade pip
RUN pip3 install --upgrade pip
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
# Needed by gateway and services files and jobs
RUN mkdir /usr/src/files/
RUN chown www-openeo:airflow /usr/src/files
