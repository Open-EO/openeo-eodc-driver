# EODC Job Service
Service for processing on the EODC infrastructure.

## Developing locally
- Login into the OpenShift instance
  ```
  oc login openshift-master.eodc.eu
  ```
- Switch to development project 
  ```
  oc project my-dev-proj
  ```
- Get names of pods
  ```
  oc get pods
  ```
- Forward ports of pods that are needed for developing (e.g. database/service)
  ```
  oc port-forward -p <pod> [<local_port>:]<pod_port> [[<local_port>:]<pod_port> ...]
  
  e.g.
  oc port-forward -p eodc-users-db-1-kp5vp 5432:5432
  ```

## Start Tests
```
python manage.py test
```

## Run Service locally
```
python manage.py runserver
```

## Important OpenShift Client commands
- Process and create service from template.json in OpenShift project
  ```
  oc project <openshift_project>
  oc process -f template.json | oc create -f -
  ```

- Delete all objects/instances 
  (Command will delete everything in project except PersistantVolumes and Secrets)
  ```
  oc delete all --all
  ```