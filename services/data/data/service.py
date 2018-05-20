from nameko.rpc import rpc
from datetime import datetime

from .dependencies.csw import CSWSession
from .schema import ProcessSchemaFull, ProcessSchema, ProcessSchemaShort
from .exceptions import NotFound, CWSError


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
