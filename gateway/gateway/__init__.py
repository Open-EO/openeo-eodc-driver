"""Initialize the Gateway.

All endpoints are added and validated on start up.
"""

from dynaconf import settings

from .dependencies.auth import TokenAuthenticationRequirement as AuthReq
from .dependencies.settings import initialise_settings
from .gateway import Gateway

# Check config variables are there and correct
initialise_settings()
if settings.ENV_FOR_DYNACONF not in ["documentation"]:

    # Firs initialise Gateway app (before other imports)
    gateway = Gateway()
    gateway.set_cors()

    from .users.service import UsersService, BasicAuthService

    # Initialize non-RPC services
    auth_service = BasicAuthService(settings.SECRET_KEY)
    users_service = UsersService()

    # Get application context and map RPCs to endpoints
    ctx, rpc = gateway.get_rpc_context()
    with ctx:

        # System endpoints
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/health",  # NB extension of openEO API
            func=gateway.send_health_check,
            rpc=False,
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/openapi",  # NB extension of openEO API
            func=gateway.send_openapi,
            rpc=False,
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/redoc",  # NB extension of openEO API
            func=gateway.send_redoc,
            rpc=False,
        )

        # Capabilities
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/",
            func=rpc.capabilities.send_index,
            validate=True,
            parse_spec=True,
        )
        gateway.add_endpoint(
            "/",  # NB: no versioning here
            func=gateway.main_page,
            rpc=False,
            parse_spec=True,
        )
        gateway.add_endpoint(
            "/.well-known/openeo",    # NB: no versioning here
            func=rpc.capabilities.get_versions,
            validate=True,
            parse_spec=True,
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/file_formats",
            func=rpc.capabilities.get_file_formats,
            validate=True,
            parse_spec=True,
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/udf_runtimes",
            func=rpc.capabilities.get_udfs,
            validate=True,
            parse_spec=True,
        )

        # EO Data Discovery
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/collections",
            func=rpc.data.get_all_products,
            validate=True,
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/collections/<collection_id>",
            func=rpc.data.get_product_detail,
            validate=True,
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/collections",  # NB extension of openEO API
            func=rpc.data.refresh_cache,
            validate=True,
            methods=["POST"],
            role="admin",
        )

        # Account Management
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/credentials/oidc",
            func=users_service.get_oidc_providers,
            rpc=False,
            auth_token=AuthReq.prohibited,
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/credentials/basic",
            func=auth_service.get_basic_token,
            rpc=False,
            validate_custom=True,
            auth_token=AuthReq.prohibited,
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/me",
            func=users_service.get_user_info,
            auth_token=AuthReq.required,
            rpc=False,
        )

        # File Management
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/files",
            func=rpc.files.get_all,
            auth_token=AuthReq.required,
            validate=True,
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/files/<path:path>",
            func=rpc.files.download,
            auth_token=AuthReq.required,
            validate=True,
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/files/<path:path>",
            func=rpc.files.upload,
            auth_token=AuthReq.required,
            validate=True,
            methods=["PUT"],
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/files/<path:path>",
            func=rpc.files.delete,
            auth_token=AuthReq.required,
            validate=True,
            methods=["DELETE"],
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/downloads/<job_id>/<path:path>",
            func=rpc.files.download_result,
            auth_token=AuthReq.required,
            validate=True,
        )

        # Process Discovery
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/processes",
            func=rpc.processes.get_all_predefined,
            validate=True,
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/processes/<process_name>",  # NB extension of openEO API
            func=rpc.processes.put_predefined,
            auth_token=AuthReq.required,
            validate=True,
            methods=["PUT"],
            role="admin",
        )

        # Process Graph Management
        # /result -> implemented under 'Job Management'
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/validation",
            func=rpc.processes.validate,
            auth_token=AuthReq.required,
            validate=True,
            methods=["POST"],
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/process_graphs",
            func=rpc.processes.get_all_user_defined,
            auth_token=AuthReq.required,
            validate=True,
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/process_graphs/<process_graph_id>",
            func=rpc.processes.get_user_defined,
            auth_token=AuthReq.required,
            validate=True,
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/process_graphs/<process_graph_id>",
            func=rpc.processes.put_user_defined,
            auth_token=AuthReq.required,
            validate=True,
            methods=["PUT"],
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/process_graphs/<process_graph_id>",
            func=rpc.processes.delete,
            auth_token=AuthReq.required,
            validate=True,
            methods=["DELETE"],
        )

        # Job Management
        # /file_formats -> implemented under 'Capabilities'
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/result",
            func=rpc.jobs.process_sync,
            auth_token=AuthReq.required,
            validate=True,
            methods=["POST"],
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/jobs",
            func=rpc.jobs.get_all,
            auth_token=AuthReq.required,
            validate=True,
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/jobs",
            func=rpc.jobs.create,
            auth_token=AuthReq.required,
            validate=True,
            methods=["POST"],
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/jobs/<job_id>",
            func=rpc.jobs.get,
            auth_token=AuthReq.required,
            validate=True,
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/jobs/<job_id>",
            func=rpc.jobs.delete,
            auth_token=AuthReq.required,
            validate=True,
            methods=["DELETE"],
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/jobs/<job_id>",
            func=rpc.jobs.modify,
            auth_token=AuthReq.required,
            validate=True,
            methods=["PATCH"],
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/jobs/<job_id>/estimate",
            func=rpc.jobs.estimate,
            auth_token=AuthReq.required,
            validate=True,
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/jobs/<job_id>/results",
            func=rpc.jobs.get_results,
            auth_token=AuthReq.required,
            validate=True,
            parse_spec=True,
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/jobs/<job_id>/results",
            func=rpc.jobs.process,
            auth_token=AuthReq.required,
            validate=True,
            methods=["POST"],
            is_async=True,
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/jobs/<job_id>/results",
            func=rpc.jobs.cancel_processing,
            auth_token=AuthReq.required,
            validate=True,
            methods=["DELETE"],
        )

        # Users Management # NB these endpoints are extensions of the openEO API
        # Users
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/users_mng/users",
            func=users_service.add_user,
            auth_token=AuthReq.required,
            rpc=False,
            validate_custom=True,
            methods=["POST"],
            role="admin",
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/users_mng/users",
            func=users_service.delete_user,
            auth_token=AuthReq.required,
            rpc=False,
            validate_custom=True,
            methods=["DELETE"],
            role="admin",
        )
        # Profiles
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/users_mng/user_profiles",
            func=users_service.add_user_profile,
            auth_token=AuthReq.required,
            rpc=False,
            validate_custom=True,
            methods=["POST"],
            role="admin",
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/users_mng/user_profiles",
            func=users_service.delete_user_profile,
            auth_token=AuthReq.required,
            rpc=False,
            validate_custom=True,
            methods=["DELETE"],
            role="admin",
        )
        # Identity Providers
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/users_mng/oidc_providers",
            func=users_service.add_identity_provider,
            auth_token=AuthReq.required,
            rpc=False,
            validate_custom=True,
            methods=["POST"],
            role="admin",
        )
        gateway.add_endpoint(
            f"/{settings.OPENEO_VERSION}/users_mng/oidc_providers",
            func=users_service.delete_identity_provider,
            auth_token=AuthReq.required,
            rpc=False,
            validate_custom=True,
            methods=["DELETE"],
            role="admin",
        )

    # Validate if the gateway was setup as defined by the OpenAPI specification
    gateway.validate_api_setup()
