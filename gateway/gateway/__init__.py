""" Initialize the Gateway """

from .gateway import Gateway

gateway = Gateway()
gateway.set_cors()

# Get application context and map RPCs to endpoints
ctx, rpc = gateway.get_rpc_context()
with ctx:

    # System endpoints
    gateway.add_endpoint("/health", func=gateway.send_health_check, rpc=False) # NB extension of openEO API
    gateway.add_endpoint("/openapi", func=gateway.send_openapi, rpc=False) # NB extension of openEO API
    gateway.add_endpoint("/redoc", func=gateway.send_redoc, rpc=False) # NB extension of openEO API

    # Capabilities
    gateway.add_endpoint("/", func=gateway.send_index, rpc=False)
    gateway.add_endpoint("/output_formats", func=gateway.get_output_formats, rpc=False)
    # /service_types

    # EO Data Discovery
    gateway.add_endpoint("/collections", func=rpc.data.get_all_products, auth=True, validate=True)
    gateway.add_endpoint("/collections/<name>", func=rpc.data.get_product_detail, auth=True, validate=True)
    # NB following route should become a process, and not be available as a route
    gateway.add_endpoint("/collections/<name>/records", func=rpc.data.get_records, auth=True, validate=True) # NB extension of openEO API
    # /subscription

    # Process Discovery
    gateway.add_endpoint("/processes", func=rpc.processes.get_all, auth=True, validate=True)
    gateway.add_endpoint("/processes", func=rpc.processes.create, auth=True, validate=True, methods=["POST"], role="admin") # NB extension of openEO API

    # Account Management
    gateway.add_endpoint("/credentials/oidc", func=gateway.send_openid_connect_discovery, rpc=False)
    # /credentials/basic
    gateway.add_endpoint("/me", func=gateway.get_user_info, rpc=False)

    # File Management
    # /files/<user_id>
    # /files/<user_id>/<path>
    # /files/<user_id>/<path> put
    # /files/<user_id>/<path> delete
    # /subscription

    # Process Graph Management
    gateway.add_endpoint("/validation", func=rpc.process_graphs.validate, auth=True, validate=True, methods=["POST"])
    # /preview
    gateway.add_endpoint("/process_graphs", func=rpc.process_graphs.get_all, auth=True, validate=True)
    gateway.add_endpoint("/process_graphs", func=rpc.process_graphs.create, auth=True, validate=True, methods=["POST"])
    gateway.add_endpoint("/process_graphs/<process_graph_id>", func=rpc.process_graphs.get, auth=True, validate=True)
    gateway.add_endpoint("/process_graphs/<process_graph_id>", func=rpc.process_graphs.modify, auth=True, validate=True, methods=["PATCH"])
    gateway.add_endpoint("/process_graphs/<process_graph_id>", func=rpc.process_graphs.delete, auth=True, validate=True, methods=["DELETE"])

    # Job Management
    # /output_formats
    # /preview
    gateway.add_endpoint("/jobs", func=rpc.jobs.get_all, auth=True, validate=True)
    gateway.add_endpoint("/jobs", func=rpc.jobs.create, auth=True, validate=True, methods=["POST"])
    gateway.add_endpoint("/jobs/<job_id>", func=rpc.jobs.get, auth=True, validate=True)
    gateway.add_endpoint("/jobs/<job_id>", func=rpc.jobs.delete, auth=True, validate=True, methods=["DELETE"])
    gateway.add_endpoint("/jobs/<job_id>", func=rpc.jobs.modify, auth=True, validate=True, methods=["PATCH"])
    # /jobs/<job_id>/estimate
    gateway.add_endpoint("/jobs/<job_id>/results", func=rpc.jobs.get_results, auth=True, validate=True)
    gateway.add_endpoint("/jobs/<job_id>/results", func=rpc.jobs.process, auth=True, validate=True, methods=["POST"], is_async=True)
    gateway.add_endpoint("/jobs/<job_id>/results", func=rpc.jobs.cancel_processing, auth=True, validate=True, methods=["DELETE"])
    # /subscription

    # Secondary Services Management
    # /service_types
    # /services
    # /services post
    # /services/<service_id>
    # /services/<service_id> patch
    # /services/<service_id> delete
    # /subscription

# Validate if the gateway was setup as defined by the OpenAPI specification
gateway.validate_api_setup()
