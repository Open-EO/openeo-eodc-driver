''' /products route of Data Service '''

from requests import get
from json import loads
from flask import Blueprint, current_app
from service.api.api_utils import parse_response

PRODUCTS_BLUEPRINT = Blueprint("products", __name__)

@PRODUCTS_BLUEPRINT.route("/products/<product_id>/pvc_id", methods=["GET"])
def get_product(product_id):
    ''' Returns the ID of the PVC containing the product. '''

    # TODO: Verify user and GET namespace + service account token of user
    namespace = "sandbox"
    auth = current_app.config["AUTH"]

    verify = current_app.config["VERIFY"]

    path = "/api/v1/namespaces/{0}/persistentvolumeclaims".format(namespace)
    url = current_app.config["OPENSHIFT_API"] + path

    response = get(url,
                   headers=auth,
                   verify=verify)

    if response.status_code != 200:
        return parse_response(400, "Could not connect to OpenShift cluster.")

    response_json = loads(response.text)
    for pvc in response_json["items"]:
        annotations = pvc["metadata"]["annotations"]

        if "eodc-product" in annotations and annotations["eodc-product"] == product_id:
            return parse_response(200, "Found product", data=pvc)

    return parse_response(404, "Could not find product")

