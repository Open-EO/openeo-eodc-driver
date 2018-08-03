""" Initialize the Gateway """

from .gateway import Gateway
gateway = Gateway()

# Get application context and map RPCs to endpoints
ctx, rpc = gateway.get_rpc_context()
with ctx:
    gateway.add_endpoint("/data", func=rpc.data.get_records, auth=True, validate=True)
    gateway.add_endpoint("/data/<data_id>", func=rpc.data.get_records, auth=True, validate=True)

# Validate if the gateway was setup as defined by the OpenAPI specification
gateway.validate_api_setup()