FROM openeo-base
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
CMD nameko run --config config.yaml data.service
