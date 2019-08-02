FROM openeo-base
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt 
USER www-openeo
CMD alembic upgrade head
CMD nameko run --config config.yaml jobs.service --backdoor 3000
