""" Initialize the Gateway """

from .gateway import Gateway

# Firs initialise Gateway app (before other imports)
gateway = Gateway()
gateway.set_cors()

from .users.service import UsersService, AuthService

# Initialize non-RPC services
auth_service = AuthService()
users_service = UsersService()

# Get application context and map RPCs to endpoints
ctx, rpc = gateway.get_rpc_context()
with ctx:

    # System endpoints
    gateway.add_endpoint("/health", func=gateway.send_health_check, rpc=False)  # NB extension of openEO API
    gateway.add_endpoint("/openapi", func=gateway.send_openapi, rpc=False)  # NB extension of openEO API
    gateway.add_endpoint("/redoc", func=gateway.send_redoc, rpc=False)  # NB extension of openEO API

    # Capabilities
    gateway.add_endpoint("/", func=rpc.capabilities.send_index, auth=False, validate=True, parse_spec=True)
    gateway.add_endpoint("/.well-known/openeo", func=rpc.capabilities.get_versions, auth=False, validate=True, parse_spec=True)
    gateway.add_endpoint("/file_formats", func=rpc.capabilities.get_file_formats, auth=False, validate=True, parse_spec=True)
    # gateway.add_endpoint("/conformance", func=rpc.capabilities)
    gateway.add_endpoint("/udf_runtimes", func=rpc.capabilities.get_udfs, auth=False, validate=True, parse_spec=True)
    gateway.add_endpoint("/service_types", func=rpc.capabilities.get_service_types, auth=False, validate=True, parse_spec=True)

    # EO Data Discovery
    gateway.add_endpoint("/collections", func=rpc.data.get_all_products, auth=False, validate=True)
    gateway.add_endpoint("/collections/<collection_id>", func=rpc.data.get_product_detail, auth=False, validate=True)
    gateway.add_endpoint("/collections", func=rpc.data.refresh_cache, auth=True, validate=True, methods=["POST"], role="admin") # NB extension of openEO API

    # Account Management
    gateway.add_endpoint("/credentials/oidc", func=users_service.get_oidc_providers, rpc=False)
    gateway.add_endpoint("/credentials/basic", func=auth_service.get_basic_token, rpc=False, validate_custom=True)
    gateway.add_endpoint("/me", func=users_service.get_user_info, auth=True, rpc=False)

    # File Management
    gateway.add_endpoint("/files", func=rpc.files.get_all, auth=True, validate=True)
    gateway.add_endpoint("/files/<path>", func=rpc.files.download, auth=True, validate=True)
    gateway.add_endpoint("/files/<path>", func=rpc.files.upload, auth=True, validate=True, methods=["PUT"])
    gateway.add_endpoint("/files/<path>", func=rpc.files.delete, auth=True, validate=True, methods=["DELETE"])
    gateway.add_endpoint("/downloads/<job_id>/<path>", func=rpc.files.download_result, auth=True, validate=True)

    # Process Discovery
    gateway.add_endpoint("/processes", func=rpc.processes.get_all_predefined, auth=False, validate=True)
    gateway.add_endpoint("/processes/<process_name>", func=rpc.processes.put_predefined, auth=True, validate=True, methods=["PUT"], role="admin") # NB extension of openEO API
    # Process Graph Management
    gateway.add_endpoint("/validation", func=rpc.processes.validate, auth=True, validate=True, methods=["POST"])
    gateway.add_endpoint("/process_graphs", func=rpc.processes.get_all_user_defined, auth=True, validate=True)
    gateway.add_endpoint("/process_graphs/<process_graph_id>", func=rpc.processes.get_user_defined, auth=True, validate=True)
    gateway.add_endpoint("/process_graphs/<process_graph_id>", func=rpc.processes.put_user_defined, auth=True, validate=True, methods=["PUT"])
    gateway.add_endpoint("/process_graphs/<process_graph_id>", func=rpc.processes.delete, auth=True, validate=True, methods=["DELETE"])
    # /result -> implemented under 'Job Management'

    # Job Management
    # /file_formats -> implemented under 'Capabilities'
    gateway.add_endpoint("/result", func=rpc.eodatareaders_rpc.process_sync, auth=True, validate=True, methods=["POST"])
    gateway.add_endpoint("/jobs", func=rpc.jobs.get_all, auth=True, validate=True)
    gateway.add_endpoint("/jobs", func=rpc.jobs.create, auth=True, validate=True, methods=["POST"])
    gateway.add_endpoint("/jobs/<job_id>", func=rpc.jobs.get, auth=True, validate=True)
    gateway.add_endpoint("/jobs/<job_id>", func=rpc.jobs.delete, auth=True, validate=True, methods=["DELETE"])
    gateway.add_endpoint("/jobs/<job_id>", func=rpc.jobs.modify, auth=True, validate=True, methods=["PATCH"])
    gateway.add_endpoint("/jobs/<job_id>/estimate", func=rpc.jobs.estimate, auth=True, validate=True)
    gateway.add_endpoint("/jobs/<job_id>/results", func=rpc.jobs.get_results, auth=True, validate=True)
    gateway.add_endpoint("/jobs/<job_id>/results", func=rpc.jobs.process, auth=True, validate=True, methods=["POST"], is_async=True)
    gateway.add_endpoint("/jobs/<job_id>/results", func=rpc.jobs.cancel_processing, auth=True, validate=True, methods=["DELETE"])

    # Secondary Services Management
    # /service_types
    # /services
    # /services post
    # /services/<service_id>
    # /services/<service_id> patch
    # /services/<service_id> delete

    # Users Management # NB these endpoints are extensions of the openEO API
    # Users
    gateway.add_endpoint("/users_mng/users", func=users_service.add_user, auth=True, rpc=False, validate_custom=True, methods=["POST"], role="admin")
    gateway.add_endpoint("/users_mng/users", func=users_service.delete_user, auth=True, rpc=False, validate_custom=True, methods=["DELETE"], role="admin")
    # Profiles
    gateway.add_endpoint("/users_mng/user_profiles", func=users_service.add_user_profile, auth=True, rpc=False, validate_custom=True, methods=["POST"], role="admin")
    gateway.add_endpoint("/users_mng/user_profiles", func=users_service.delete_user_profile, auth=True, rpc=False, validate_custom=True, methods=["DELETE"], role="admin")
    # Identity Providers
    gateway.add_endpoint("/users_mng/oidc_providers", func=users_service.add_identity_provider, auth=True, rpc=False, validate_custom=True, methods=["POST"], role="admin")
    gateway.add_endpoint("/users_mng/oidc_providers", func=users_service.delete_identity_provider, auth=True, rpc=False, validate_custom=True, methods=["DELETE"], role="admin")


# Validate if the gateway was setup as defined by the OpenAPI specification
gateway.validate_api_setup()
