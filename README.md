# openEO: OpenShift Driver

## Information
- version: 0.0.1
- Python: 3.6.2
- Databases: Postgres, Redis
- Dependencies: Flask, Celery

The openEO OpenShift driver provides openEO API functionality on top of RedHat's OpenShift Origin.
A flask REST client on route /jobs is provided. The job execution can be distributed on multiple workers using Celery.

For more information on OpenShift please visit:
- [OpenShift Origin website](https://www.openshift.org/)
- [OpenShift Origin documentation](https://docs.openshift.org/latest/welcome/index.html)
- [How to setup an OpenShift cluster](https://docs.openshift.org/latest/install_config/install/planning.html)

## Installation
### Template File
The template file (template.json) is an OpenShift descriptive file that is used to implement an environment and its parameterized objects.
A template can be processed and the included objects will be created in the project namespace.
The openEO Openshift template file uses references to the public git repository to build and deploy the required services (/services).
For further information please visit: [OpenShift Templates](https://docs.openshift.org/latest/dev_guide/templates.html)

### Requirements
- For the installation and running of the openEO instance a OpenShift cluster with accessible OpenShift APi must be setup. (See: [Installing a cluster](https://docs.openshift.com/container-platform/3.7/install_config/install/planning.html)
- The OpenShift cluster needs to have persitant volumes avaiable and a storage class to access the storage (See: [Configure Persistant Storage](https://docs.openshift.com/container-platform/3.7/install_config/persistent_storage/index.html)
- The OpenShift Client Tools must be installed (See: [OpenShift client tools download](https://www.openshift.org/download.html))

### Installation Steps
- Log into OpenShift instance usuing OpenShift Client Tools (oc): ```oc login <openshift_api_url>```
- Create new project for openEO: ```oc new-project <openeo_project_name>```
- Create new project for job execution: ```oc new-project <execution_project_name>```
- Create a service account: ```oc create serviceaccount robot```
- Grant admin role to service account: ```oc policy add-role-to-user admin system:serviceaccounts:test:robot```
- Fill out parameters in OpenShift template file (template.json)
- Change to the created OpenShift openEO project: ```oc project <openeo_project_name>```
- Download the template.json from the git repository
- Process the template and create objects: ```oc process template.json | oc create -f -```
- The project will now be setup in the openeo namespace and can be accesses over the host name that was specified in the template file

### Parameters
- EXECUTION_NAMESPACE:
  Namspace of OpenSHift project for job execution (e.g. "execution-environment")
- SERVICEACCOUNT_TOKEN:
  Permanent token of a service account in the execution namespace that can bus used to access the OpenShift API
- STORAGE_CLASS:
  Storage class for PersitantVolumeClaims that should be used (e.g. "storage-write")
- OPENEO_API
  URI for accessing the openEO API (e.g. http://openeo.example.com)
- OPENSHIFT_API
  URI for accessing the OpenShift API (e.g. http://openshift.example.com)
- CSW_SERVER
  URI for accessing CSW server (e.g. http://csw.example.com)

## Contributing
### Developing Locally
MiniShift is a tool for local development by launching a single node OpenShift cluster. It can be downloaded at [MiniShift](https://www.openshift.org/minishift/)
Furthermore, for developing locally on an external cluster the port of the pods in the project namespace can be forwarded to a local machine:
- Login into the OpenShift instance: ```oc login <openshift_api_url>```
- Switch to openEO project: ```oc project <openeo_project_name>```
- Get names of pods in project: ```oc get pods```
- Forward ports of pods that are needed for developing (e.g. database/service): ```oc port-forward <pod> [<local_port>:]<pod_port> [[<local_port>:]<pod_port> ...]```
- E.g. ```oc port-forward -p openeo-user-postgres-1-s2da 5432:5432```

### Further Commands:
- Delete all objects in namespace (except secrets and pvcs): ```oc delete all --all```
- Run service test: ```python manage.py test```
- Run service locally: ```python manage.py runserver```
- Recreate service database: ```python manage.py recreate_db```
- Seed service database: ```python manage.py seed_db```
- Drop service database: ```python manage.py drop_db```
- Migrate service database: ```python manage.py db migrate```
- Upgrade service database: ```python manage.py db upgrade```
