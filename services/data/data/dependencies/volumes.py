from nameko.extensions import DependencyProvider


class VolumeCreator(DependencyProvider):
    def get_dependency(self, worker_ctx):
        return CSWHandler(environ.get("CSW_SERVER"))