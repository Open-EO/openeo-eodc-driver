FROM openeo-base
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
RUN mkdir /usr/src/api
EXPOSE 5000
CMD nameko run --config config.yaml capabilities.service --backdoor 3000
