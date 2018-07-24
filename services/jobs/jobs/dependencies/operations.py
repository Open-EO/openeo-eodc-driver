from nameko.extensions import DependencyProvider

class OperationsHandler:

    operations = {
        "min_time": self.min_time,
        "ndvi": self.ndvi,
        "filter_bbox": self.filter_bbox,
        "filter_bands": self.filter_bands
    }

    def filter_bbox(self, args, vrt):
        #TODO
        return vrt.append(["filter_bbox", args])
    
    def filter_bands(self, args, vrt):
        #TODO
        return vrt.append(["filter_bands", args])
    
    def ndvi(self, args, vrt):
        #TODO
        return vrt.append(["ndvi", args])
    
    def min_time(self, args, vrt):
        #TODO
        return vrt.append(["min_time", args])
    
    def map_operation(self, process_id, args, vrt):
        return self.operations["process_id"](args, vrt)

class Operations(DependencyProvider):
    def get_dependency(self, worker_ctx):
        return OperationsHandler()