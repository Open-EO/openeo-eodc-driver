from nameko.rpc import rpc
from .dependencies.csw import CSWSession
from .dependencies.arg_parser import ArgValidatorProvider
from .exceptions import CWSError, ValidationError


class DataService:
    name = "data"

    arg_parser = ArgValidatorProvider()
    csw_session = CSWSession()

    @rpc
    def health(self, request):
        return { "status": "success"}
    
    @rpc
    def get_records(self, qtype="products", qname="", qgeom="", qstartdate="", qenddate=""):
        try:
            product, bbox, start, end = self.arg_parser.parse(qname, qgeom, qstartdate, qenddate) 
            results = self.csw_session.get_data(qtype, product, bbox, start, end)

            return {
                "status": "success",
                "data": results
            }
        except (ValidationError, CWSError) as exp:
            return {"status": "error", "service": self.name, "key": "BadRequest", "msg": str(exp)}
        except Exception as exp: 
            return {"status": "error", "service": self.name, "key": "InternalServerError", "msg": str(exp)}
