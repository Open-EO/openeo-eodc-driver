FROM openeo-base
COPY requirements.txt .
COPY run.sh .
RUN python3 -m pip install -r requirements.txt
USER www-openeo
CMD ["./run.sh"]
