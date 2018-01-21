''' Benchmark Test File '''

from create import create_object, CreationError
from parameters import SOURCE_REPOSITORY_URL, SOURCE_REPOSITORY_REF, GITHUB_WEBHOOK_SECRET

try:
    create_object("image_stream_1.json", "imagestreams")
    create_object("image_stream_2.json", "imagestreams")
    create_object("build_config.json", "buildconfigs", parameters=(
        SOURCE_REPOSITORY_URL, SOURCE_REPOSITORY_REF, GITHUB_WEBHOOK_SECRET))
    create_object("service.json", "services", api_name="api")
    create_object("deployment_config.json", "deploymentconfigs")
    create_object("route.json", "routes")
except FileNotFoundError as exp:
    print(exp)
except CreationError as exp:
    print(exp)
