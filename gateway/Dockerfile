FROM openeo-base
COPY requirements.txt .
RUN  python3 -m pip install -r requirements.txt
CMD python3 manage.py prod -b $HOST:$GATEWAY_PORT -w $NO_WORKERS
