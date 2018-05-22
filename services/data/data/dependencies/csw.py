from os import environ
from requests import post
from json import loads, dumps
from datetime import datetime, timedelta
from xml.dom.minidom import parseString
from shapely.geometry.base import geom_from_wkt, WKTReadingError
from nameko.extensions import DependencyProvider

from .bands import BandsExtractor
from ..exceptions import CWSError
from .xml_templates import xml_base, xml_and, xml_series, xml_product, xml_begin, xml_end, xml_bbox
from .products import products # TODO: Just temporary because csw request is currently very slow

class CSWHandler:
    def __init__(self, csw_server):
        self.csw_server = csw_server
        self.bands_extractor = BandsExtractor()
        self.map_types = {
            "products": self.get_products,
            "product_details": self.get_product_details,  
            "full": self.get_records_full, 
            "short": self.get_records_shorts, 
            "file_paths": self.get_file_paths
        }
    
    def get_data(self, qtype, qname, qgeom, qstartdate, qenddate):
        return self.map_types[qtype](product=qname, bbox=qgeom, begin=qstartdate, end=qenddate)
    
    def poly_to_bbox(self, wkt_string):
        """
        Gets the bounding box of the dataset from from wkt_geometry.
        """
        poly = geom_from_wkt("POLYGON" + wkt_string)
        return list(poly.bounds)

    def get_records(self, series=False, product=False, begin=False, end=False, bbox=False, just_filepaths=False):
        """ 
        Return the collected csw records of the query 
        """

        output_schema = "http://www.opengis.net/cat/csw/2.0.2" if series is True else "http://www.isotc211.org/2005/gmd"

        xml_filters = []
        if series: 
            xml_filters.append(xml_series)

        if product:
            if series:
                xml_filters.append(xml_product.format(property="dc:identifier", product=product))
            else:
                xml_filters.append(xml_product.format(property="apiso:ParentIdentifier", product=product))

        if begin:
            try:
                datetime.strptime(begin, '%Y-%m-%d')
            except ValueError:
                raise CWSError("Wrong format of begin date.")

            begin += "T00:00:00Z"
            xml_filters.append(xml_begin.format(begin=begin))

        if end: 
            try:
                datetime.strptime(end, '%Y-%m-%d')
            except ValueError:
                raise CWSError("Wrong format of end date.")

            end += "T23:59:59Z"

            if not series:
                xml_filters.append(xml_end.format(end=end))

        if bbox: 
            if isinstance(bbox, str):
                try:
                    bbox = self.poly_to_bbox(bbox)
                except WKTReadingError:
                    raise CWSError("Wrong format of WKT polygon.")

            if isinstance(bbox, list) and len(bbox) == 4:
                xml_filters.append(xml_bbox.format(bbox=bbox))
            else:
                raise CWSError("Invalid format of BBox")
            
        if len(xml_filters) == 0:
            return []
        
        filter_parsed = ""
        if len(xml_filters) == 1:
            filter_parsed = xml_filters[0]
        else:
            tmp_filter = ""
            for xml_filter in xml_filters:
                tmp_filter += xml_filter
            filter_parsed = xml_and.format(children=tmp_filter)

        all_records = []
        record_next = 1
        while int(record_next) > 0:
            record_next, records = self.get_single_records(record_next, filter_parsed, output_schema, just_filepaths)
            all_records += records
        
        return all_records

    def get_single_records(self, start_position, filter_parsed, output_schema, just_filepaths):
        ''' Return the records of a single request '''
        
        xml_request = xml_base.format(children=filter_parsed, output_schema=output_schema, start_position=start_position)
        response = post(self.csw_server, data=xml_request)

        if not response.ok:
            print("Server Error {0}: {1}".format(response.status_code, response.text))
            raise CWSError("Error while communicating with CSW server.")

        if response.text.startswith("<?xml"):
            xml = parseString(response.text)
            print("{0}".format(xml.toprettyxml()))
            raise CWSError("Error while communicating with CSW server.")

        response_json = loads(response.text)

        if "ows:ExceptionReport" in response_json:
            print("{0}".format(dumps(response_json, indent=4, sort_keys=True)))
            raise CWSError("Error while communicating with CSW server.")

        search_result = response_json["csw:GetRecordsResponse"]["csw:SearchResults"]

        record_next = search_result["@nextRecord"]

        if "gmd:MD_Metadata" in search_result:
            records = search_result["gmd:MD_Metadata"]
        elif "csw:Record" in search_result:
            records = search_result["csw:Record"]
        else:
            record_next = 0
            records = []

        if not isinstance(records, list):
            records = [records]

        return record_next, records

    def get_products(self, product, begin, end, bbox):
        # records = self.get_records(
        #     series=True, 
        #     product=product, 
        #     begin=begin, 
        #     end=end, 
        #     bbox=bbox)
        
        # results = []
        # for item in records:
        #     results.append({
        #         "product_id": item["dc:identifier"],
        #         "description": item["dct:abstract"],
        #         "source": item["dc:creator"]
        #     })

        # TODO: Just temporary because csw request is currently very slow
        return products #results
    
    def get_product_details(self, product, begin, end, bbox):
        record = self.get_records(
            series=True, 
            product=product, 
            begin=begin, 
            end=end, 
            bbox=bbox)[0]

        upper = record["ows:BoundingBox"]["ows:UpperCorner"].split(" ")
        lower = record["ows:BoundingBox"]["ows:LowerCorner"].split(" ")
        dumped_result = {
            "product_id": record["dc:identifier"],
            "description": record["dct:abstract"],
            "source": record["dc:creator"],
            "extent": {
                "srs": "EPSG:4326",
                "left": lower[0],
                "right": upper[0],
                "bottom": lower[1],
                "top": upper[1]
            },
            "time": {
                "from": record["dc:date"],
                "to": datetime.now().strftime('%Y-%m-%d')
            },
            "bands": self.bands_extractor.get_bands(product)
        }

        return dumped_result

    def get_records_full(self, product, begin, end, bbox):
        results = self.get_records(
            series=False, 
            product=product, 
            begin=begin, 
            end=end, 
            bbox=bbox)

        return results

    def get_records_shorts(self, product, begin, end, bbox):
        records = self.get_records(
            series=False, 
            product=product, 
            begin=begin, 
            end=end, 
            bbox=bbox)
        
        results = []
        for item in records:
            path = item["gmd:fileIdentifier"]["gco:CharacterString"]
            name = path.split("/")[-1].split(".")[0]

            extend = item["gmd:identificationInfo"]["gmd:MD_DataIdentification"]["gmd:extent"]["gmd:EX_Extent"]
            spatial_extend = extend["gmd:geographicElement"]["gmd:EX_GeographicBoundingBox"]
            spatial = {
                "east": spatial_extend["gmd:eastBoundLongitude"]["gco:Decimal"],
                "north": spatial_extend["gmd:northBoundLatitude"]["gco:Decimal"],
                "south": spatial_extend["gmd:southBoundLatitude"]["gco:Decimal"],
                "west": spatial_extend["gmd:westBoundLongitude"]["gco:Decimal"]
            }
            
            temporal_extend = extend["gmd:temporalElement"]["gmd:EX_TemporalExtent"]["gmd:extent"]["gml:TimePeriod"]
            temporal = {
                "begin": temporal_extend["gml:beginPosition"],  # datetime.strptime(temporal_extend["gml:endPosition"], '%Y-%m-%dT%H:%M:%S.%fZ')
                "end": temporal_extend["gml:endPosition"]
            }

            results.append(
                {
                    "name": name,
                    "temporal": temporal,
                    "spatial": spatial,
                    "path": path
                })

        return results

    def get_file_paths(self, product, begin, end, bbox):
        ''' Get file paths from records '''

        # TODO: Do we need a time extension?
        # start_date = datetime.strptime(begin, '%Y-%m-%d')
        # start_date = start_date - timedelta(days=1)
        # start_date = start_date.strftime("%Y-%m-%dT00:00:00Z")
        
        # end_date = datetime.strptime(end, '%Y-%m-%d')
        # end_date = end_date + timedelta(days=1)
        # end_date = end_date.strftime("%Y-%m-%dT23:59:59Z")

        records = self.get_records(
            series=False, 
            product=product, 
            begin=begin, 
            end=end, 
            bbox=bbox, 
            just_filepaths=True)

        results = []
        for item in records:
            path = item["gmd:fileIdentifier"]["gco:CharacterString"]
            name = path.split("/")[-1].split(".")[0]
            date = item["gmd:identificationInfo"]["gmd:MD_DataIdentification"]["gmd:extent"]["gmd:EX_Extent"]["gmd:temporalElement"]["gmd:EX_TemporalExtent"]["gmd:extent"]["gml:TimePeriod"]["gml:beginPosition"][0:10]

            results.append(
                {
                    "name": name,
                    "date": date,
                    "path": path
                })

        return results

class CSWSession(DependencyProvider):
    def get_dependency(self, worker_ctx):
        return CSWHandler(environ.get("CSW_SERVER"))