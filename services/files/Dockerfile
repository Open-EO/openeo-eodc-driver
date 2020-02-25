FROM openeo-base
COPY requirements.txt .
COPY run.sh .
RUN python3 -m pip install -r requirements.txt
RUN mkdir /usr/src/files
USER www-openeo
CMD ["./run.sh"]
