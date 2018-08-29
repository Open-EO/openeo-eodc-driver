""" Initialize the Gateway """

from .gateway import Gateway

gateway = Gateway()
gateway.set_cors()

# Get application context and map RPCs to endpoints
ctx, rpc = gateway.get_rpc_context()
with ctx:
    gateway.add_endpoint("/data", func=rpc.data.get_all_products, auth=True, validate=True)
    gateway.add_endpoint("/data/<data_id>", func=rpc.data.get_product_detail, auth=True, validate=True)
    gateway.add_endpoint("/data/<data_id>/records", func=rpc.data.get_records, auth=True, validate=True)
    gateway.add_endpoint("/processes", func=rpc.processes.get_processes, auth=True, validate=True)
    gateway.add_endpoint("/processes", func=rpc.processes.create_process, auth=True, validate=True, methods=["POST"], role="admin")
    gateway.add_endpoint("/jobs", func=rpc.jobs.get_jobs, auth=True, validate=True)

# Validate if the gateway was setup as defined by the OpenAPI specification
gateway.validate_api_setup()
