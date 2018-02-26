# openEO: OpenShift Driver

## Information
- version: 0.0.1
- Python: 3.6.2
- Databases: Postgres ()
- Dependencies: Flask, Celery

The openEO OpenShift driver provides openEO API functionality on top of RedHat's OpenShift Origin.
A flask REST client on route /jobs is provided. The job execution can be distributed on multiple workers using Celery.

For more information on OpenShift please visit:
- (OpenShift Origin website)[https://www.openshift.org/]
- (OpenShift Origin documentation)[https://docs.openshift.org/latest/welcome/index.html]
- (How to setup an OpenShift cluster)[https://docs.openshift.org/latest/install_config/install/planning.html]

## Installation
### Requirements
- For the installation and running of the openEO instance a OpenShift cluster with accessible OpenShift APi must be setup. (See: (Installing a cluster)[https://docs.openshift.com/container-platform/3.7/install_config/install/planning.html])
- The OpenShift cluster needs to have persitant volumes avaiable and a storage class to access the storage (See: (Configure Persistant Storage)[https://docs.openshift.com/container-platform/3.7/install_config/persistent_storage/index.html])
- The OpenShift Client Tools must be installed (See: (OpenSHift OC Download)[https://www.openshift.org/download.html])
- 

### job service installation steps
- Log into OpenShift instance usuing OpenShift Client Tools (oc): ```oc login <openshift_url>```
- Create new project/namespace for the job service: ```oc new-project <project_name>```
- Create new project/namespace for job execution: ```oc new-project <project_name>```
- Create a service account: ```oc create serviceaccount robot```
- Grant admin role to service account: ```oc policy add-role-to-user admin system:serviceaccounts:test:robot```

### Environmental Variables
- EXECUTION_NAMESPACE:
  Namspace of OpenSHift project for job execution (e.g. "execution-environment")
- SERVICEACCOUNT_TOKEN:
  Permanent token of a service account in the execution namespace that can bus used to access the OpenShift API
- STORAGE_CLASS:
  Storage class for PersitantVolumeClaims that should be used (e.g. "storage-write")
- OPENEO_API
  URI for accessing the OpenEO API (e.g. http://openeo.example.com)
- OPENSHIFT_API
  URI for accessing the OpenShift API (e.g. http://openshift.example.com)
- CSW_SERVER
  URI for accessing CSW server (e.g. http://csw.example.com)


### Developing locally
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

## Commands
- Start Tests: python manage.py test
```

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