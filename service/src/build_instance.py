''' Build Class of the EODC Template Engine  '''

from service.src.exceptions import TemplateException, BuildException
from service.src.templates.image_stream import ImageStream
from service.src.templates.build_config import BuildConfig

class BuildInstance:
    ''' BuildInstance class has the templates of the build and handles execution. '''

    def __init__(self, payload):

        if "image_stream" not in payload:
            raise BuildException("Missing ImageStream Configurations.")
        if "build_config" not in payload:
            raise BuildException("Missing BuildConfig Configurations.")

        try:
            self.image_stream = ImageStream(payload["image_stream"])
            self.build_config = BuildConfig(payload["build_config"])
        except TemplateException as exp:
            raise BuildException("Exeption in Build instantiation: " + str(exp))

    def perform_build(self):
        ''' Performs build of the job '''

        try:
            self.image_stream.execute()
            name, self_link = self.build_config.execute()["metadata"]["selfLink"]
        except TemplateException as exp:
            raise BuildException("Exception in Build execution: " + str(exp))

        return name, self_link