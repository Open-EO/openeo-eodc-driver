from nameko.rpc import rpc
from datetime import datetime

from .dependencies.csw import CSWSession
from .exceptions import CWSError


class DataService:
    name = "data"

    csw_session = CSWSession()

    @rpc
    def health(self):
        return {"status": "success"}
    
    @rpc
    def get_records(self, qtype="products", qname="", qgeom="", qstartdate="", qenddate=""):
        try:
            results = self.csw_session.get_data(qtype, qname, qgeom, qstartdate, qenddate)

            return {
                "status": "success",
                "data": results
            }
        except CWSError: 
            return {"status": "error", "exc_key":  "BadRequest"}
        except Exception as exp:
            return {"status": "error", "exc_key":  "InternalServerError"}
    
    @rpc
    def prepare_data(self, qname="", qgeom="", qstartdate="", qenddate=""):
        try:
            file_paths = self.csw_session.get_data("file_paths", qname, qgeom, qstartdate, qenddate)
            volume_path = self.




            return {
                "status": "success",
                "data": "results"
            }
        except CWSError: 
            return {"status": "error", "exc_key":  "BadRequest"}
        except Exception as exp:
            return {"status": "error", "exc_key":  "InternalServerError"}
