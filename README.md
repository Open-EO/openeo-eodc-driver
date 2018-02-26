# openEO: OpenShift Driver

## Information
- version: 0.0.1
- Python: 3.6.2
- Databases: Postgres ()
- Dependencies: Flask, Celery

The openEO OpenShift driver provides openEO API functionality on top of RedHat's OpenShift Origin.
A flask REST client on route /jobs is provided. The job execution can be distributed on multiple workers using Celery

For more information on OpenShift please visit:
- (OpenShift Origin website)[https://www.openshift.org/]
- (OpenShift Origin documentation)[https://docs.openshift.org/latest/welcome/index.html]
- (How to setup an OpenShift cluster)[https://docs.openshift.org/latest/install_config/install/planning.html]

## Environmental Variables

## Installation
- Log into OpenShift instance usuing OpenShift Client Tools (oc): ``` oc login <openshift_url> ```
- Create new project: ``` oc new-project <project_name> --description="<description>" --display-name="<display_name>" ```
- 

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