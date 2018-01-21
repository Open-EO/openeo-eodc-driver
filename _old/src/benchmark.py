''' Benchmark Test File '''

from api_requests import create_object, patch_object, delete_object, CreationError
from parameters import SOURCE_REPOSITORY_URL, SOURCE_REPOSITORY_REF, GITHUB_WEBHOOK_SECRET

try:
    create_object("image_stream.json", "imagestreams")
    create_object("build_config.json", "buildconfigs", parameters=(
        SOURCE_REPOSITORY_URL, SOURCE_REPOSITORY_REF, GITHUB_WEBHOOK_SECRET))
    create_object("service.json", "services", api="api")
    create_object("deployment_config.json", "deploymentconfigs")
    create_object("route.json", "routes")

    # delete_object("deploymentconfigs", "eodc-benchmark")
    # patch_object("deployment_config.json", "deploymentconfigs", "eodc-benchmark")
except FileNotFoundError as exp:
    print(exp)
except CreationError as exp:
    print(exp)
