FROM openeo-base
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt 
EXPOSE 5000
CMD nameko run --config config.yaml jobs.service --backdoor 3000