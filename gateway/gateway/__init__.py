""" Initialize the Gateway """

from .gateway import Gateway

gateway = Gateway()
gateway.set_cors()

# Get application context and map RPCs to endpoints
ctx, rpc = gateway.get_rpc_context()
with ctx:
    gateway.add_endpoint("/collections", func=rpc.data.get_all_products, auth=False, validate=True)
    gateway.add_endpoint("/collections/<name>", func=rpc.data.get_product_detail, auth=False, validate=True)
    gateway.add_endpoint("/collections/<name>/records", func=rpc.data.get_records, auth=False, validate=True)
    gateway.add_endpoint("/processes", func=rpc.processes.get_all, auth=False, validate=True)
    gateway.add_endpoint("/processes", func=rpc.processes.create, auth=False, validate=True, methods=["POST"], role="admin")
    gateway.add_endpoint("/process_graphs", func=rpc.process_graphs.get_all, auth=False, validate=True)
    gateway.add_endpoint("/process_graphs", func=rpc.process_graphs.create, auth=False, validate=True, methods=["POST"])
    gateway.add_endpoint("/process_graphs/<process_graph_id>", func=rpc.process_graphs.get, auth=False, validate=True)
    gateway.add_endpoint("/process_graphs/<process_graph_id>", func=rpc.process_graphs.modify, auth=False, validate=True, methods=["PATCH"])
    gateway.add_endpoint("/process_graphs/<process_graph_id>", func=rpc.process_graphs.delete, auth=False, validate=True, methods=["DELETE"])
    gateway.add_endpoint("/validation", func=rpc.process_graphs.validate, auth=False, validate=True, methods=["POST"])
    gateway.add_endpoint("/jobs", func=rpc.jobs.get_all, auth=False, validate=True)
    gateway.add_endpoint("/jobs", func=rpc.jobs.create, auth=False, validate=True, methods=["POST"])
    gateway.add_endpoint("/jobs/<job_id>", func=rpc.jobs.get, auth=False, validate=True)
    gateway.add_endpoint("/jobs/<job_id>", func=rpc.jobs.delete, auth=False, validate=True, methods=["DELETE"])
    gateway.add_endpoint("/jobs/<job_id>", func=rpc.jobs.modify, auth=False, validate=True, methods=["PATCH"])
    gateway.add_endpoint("/jobs/<job_id>/results", func=rpc.jobs.get_results, auth=False, validate=True)
    gateway.add_endpoint("/jobs/<job_id>/results", func=rpc.jobs.process, auth=False, validate=True, methods=["POST"], is_async=True)
    gateway.add_endpoint("/jobs/<job_id>/results", func=rpc.jobs.cancel_processing, auth=False, validate=True, methods=["DELETE"])

# Validate if the gateway was setup as defined by the OpenAPI specification
gateway.validate_api_setup()
