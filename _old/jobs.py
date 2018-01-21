''' Benchmark service '''

from flask import Blueprint, request
from service.api.utils import parse_response
from service.src.api_requests import create_object, patch_object, delete_object, CreationError
from flask import current_app
from service.tasks.benchmark import perform_benchmarking


JOBS_BLUEPRINT = Blueprint("jobs", __name__)


@ JOBS_BLUEPRINT.route("/jobs/benchmark", methods=["POST"])
def perform_benchmark_job():
    ''' Add a benchmarking job '''

    post_data = request.get_json()

    if not post_data:
        return parse_response(400, "Invalid payload.")

    try:
        settings = {
            "openshift_api_url": current_app.config.get('OPENSHIFT_API_URL'),
            "openshift_api_token": current_app.config.get('OPENSHIFT_API_TOKEN'),
            "openshift_api_namespace": current_app.config.get('OPENSHIFT_API_NAMESPACE'),
            "git_url": post_data["git_url"],
            "git_ref": post_data["git_ref"],
            "min_cpu": post_data["min_cpu"],
            "max_cpu": post_data["max_cpu"],
            "min_memory": post_data["min_memory"],
            "max_memory": post_data["max_memory"]
        }

        perform_benchmarking.delay(settings)

        # create_object("image_stream.json", "imagestreams")
        # create_object("image_stream_cadvisor.json", "imagestreams")
        # create_object("build_config.json", "buildconfigs", parameters=(post_data["url"], post_data["ref"], "GITHUB_WEBHOOK_SECRET"))
        # create_object("service.json", "services", api="api")
        # create_object("deployment_config.json", "deploymentconfigs", parameters=(post_data["limit_cpu"], post_data["limit_memory"], post_data["requests_cpu"], post_data["requests_memory"]))
        # create_object("route.json", "routes")
        # delete_object("deploymentconfigs", "eodc-benchmark")
        # patch_object("deployment_config.json", "deploymentconfigs", "eodc-benchmark")

        return parse_response(201, "Job sucessfully created!")
    except FileNotFoundError as exp:
        print(exp)
        return parse_response(400, "Could not process job!")
    except CreationError as exp:
        print(exp)
        return parse_response(400, "Could not process job!")
    except ValueError as exp:
        print(exp)
        return parse_response(400, "Could not process job!")