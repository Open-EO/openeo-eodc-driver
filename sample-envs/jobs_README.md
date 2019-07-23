## For local development only

You need to find on which IP is the airflow webserver running on. Make sure you already run docke-compose up from the airflow subfolder. Then run the following:
```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' airflow_webserver
```

The inside `jobs.env` set AIRFLOW_HOST preceded by 'http://' and append the port ':8080', for example: AIRFLOW_HOST=http://172.18.0.12:8080
