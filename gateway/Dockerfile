FROM openeo-base
COPY requirements.txt .
RUN  python3 -m pip install -r requirements.txt
USER www-openeo
CMD python3 manage.py runserver -h $HOST -p $GATEWAY_PORT
