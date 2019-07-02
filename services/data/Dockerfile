FROM openeo-base
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
ADD . /usr/src/app
CMD nameko run --config config.yaml data.service