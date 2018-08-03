from nameko.rpc import rpc
from .dependencies.csw import CSWSession
from .dependencies.arg_parser import ArgValidatorProvider
from .exceptions import CWSError, ValidationError


class DataService:
    name = "data"

    arg_parser = ArgValidatorProvider()
    csw_session = CSWSession()
    
    @rpc
    def get_records(self, user_id=None, qtype="products", data_id="", qgeom="", qstartdate="", qenddate=""):
        try:
            product, bbox, start, end = self.arg_parser.parse(data_id, qgeom, qstartdate, qenddate) 
            results = self.csw_session.get_data(qtype, product, bbox, start, end)

            return {
                "status": "success",
                "data": results
            }
        except (ValidationError, CWSError) as exp:
            return {
                "status": "error", 
                "service": self.name, 
                "user_id": user_id, 
                "code": 400, 
                "msg": str(exp),
                "internal":False, 
                "links": "http://docs.api.eodc.eu/tbd"
                }
        except Exception as exp: 
            return {
                "status": "error", 
                "service": self.name, 
                "user_id": user_id, 
                "code": 500, 
                "msg": str(exp),
                "internal":True,
                "links": "http://docs.api.eodc.eu/tbd"}
