FROM openeo-base
COPY requirements.txt .
RUN  python3 -m pip install -r requirements.txt
ADD . /usr/src/app
CMD python3 manage.py runserver -h $HOST -p $GATEWAY_PORT