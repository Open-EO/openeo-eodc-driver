FROM openeo-base
RUN mkdir /usr/src/files
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
EXPOSE 5000
CMD nameko run --config config.yaml files.service --backdoor 3000
