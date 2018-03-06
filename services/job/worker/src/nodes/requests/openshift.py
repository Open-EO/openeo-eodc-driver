from os import environ
from utils import send_post

# OPENSHIFT_URL = environ.get("OPENSHIFT_API")
# OPENSHIFT_AUTH = auth = {"Authorization": "Bearer " + environ.get("SERVICEACCOUNT_TOKEN")}
# OPENSHIFT_NAMESPACE = environ.get("EXECUTION_NAMESPACE")
# OPENSHIFT_STORAGE_CLASS = environ.get("STORAGE_CLASS")
# OPENSHIFT_VERIFY =  True if environ.get("VERIFY") == "true" else False

# def execute_template(path, template):
#     url = "{0}/{1}".format(OPENSHIFT_URL, path)
#     send_post(url, template, OPENSHIFT_AUTH, OPENSHIFT_VERIFY)



#     url = environ.get("OPENSHIFT_API") + self.path
#     response = post(url, data=self.get_json(), headers=auth, verify=verify)



# verify =

# # Execute template



# if response.ok == False:
#     self.raise_error(response.text)

# self.status = "Created"