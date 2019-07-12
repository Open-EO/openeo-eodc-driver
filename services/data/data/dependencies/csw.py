""" CSW Session """

from os import environ, path
from requests import post
from json import loads, dumps
from datetime import datetime, timedelta
from xml.dom.minidom import parseString
from nameko.extensions import DependencyProvider

from ..models import ProductRecord, Record, FilePath, SpatialExtent, TemporalExtent
from .xml_templates import xml_base, xml_and, xml_series, xml_product, xml_begin, xml_end, xml_bbox
from .bands import BandsExtractor


class CWSError(Exception):
    ''' CWSError raises if a error occures while querying the CSW server. '''

    def __init__(self, msg: str=""):
        super(CWSError, self).__init__(msg)


class CSWHandler:
    """The CSWHandler instances are responsible for communicating with the CSW server,
    including parsing a XML request, parsing the response and mapping the values to the
    required output format.
    """

    def __init__(self, csw_server_uri: str, cache_path: str):
        self.csw_server_uri = csw_server_uri
        self.cache_path = cache_path
        self.bands_extractor = BandsExtractor()

    def get_all_products(self) -> list:
        """Returns all products available at the back-end.

        Returns:
            list -- The list containing information about available products
        """

        data = self._get_records(series=True)

        # product_records = []
        # for product_record in data:
        #     product_records.append(
        #         ProductRecord(
        #             data_id=product_record["dc:identifier"],
        #             description=product_record["dct:abstract"],
        #             source=product_record["dc:creator"])
        #         )

        # return product_records
        return data

    def get_product(self, data_id: str) -> dict:
        """Returns information about a specific product.

        Arguments:
            data_id {str} -- The identifier of the product

        Returns:
            dict -- The product data
        """

        data = self._get_records(data_id, series=True)[0]

        # upper = data["ows:BoundingBox"]["ows:UpperCorner"].split(" ")
        # lower = data["ows:BoundingBox"]["ows:LowerCorner"].split(" ")

        # product_record = ProductRecord(
        #     data_id=data["dc:identifier"],
        #     description=data["dct:abstract"],
        #     source=data["dc:creator"],
        #     spatial_extent=SpatialExtent(
        #         top=upper[1],
        #         bottom=lower[1],
        #         left=lower[0],
        #         right=upper[0],
        #         crs="EPSG:4326"
        #     ),
        #     temporal_extent="{0}/{1}".format(data["dc:date"], 
        #                                      datetime.now().strftime('%Y-%m-%d')),
        #     bands=self.bands_extractor.get_bands(data_id)
        # )
        # return product_record
        return data

    def get_records_full(self, product: str, bbox: list, start: str, end: str) -> list:
        """Returns the full information of the records of the specified products
        in the temporal and spatial extents.

        Arguments:
            product {str} -- The identifier of the product
            bbox {list} -- The spatial extent of the records
            start {str} -- The start date of the temporal extent
            end {str} -- The end date of the temporal extent

        Returns:
            list -- The records data
        """

        return self._get_records(product, bbox, start, end)

    def get_records_shorts(self, product: str, bbox: list, start: str, end: str) -> list:
        """Returns the short information of the records of the specified products
        in the temporal and spatial extents.

        Arguments:
            product {str} -- The identifier of the product
            bbox {list} -- The spatial extent of the records
            start {str} -- The start date of the temporal extent
            end {str} -- The end date of the temporal extent

        Returns:
            list -- The records data
        """

        data = self._get_records(product, bbox, start, end)

        response = []
        for item in data:
            path = item["gmd:distributionInfo"]["gmd:MD_Distribution"]["gmd:transferOptions"][
                "gmd:MD_DigitalTransferOptions"]["gmd:onLine"][0]["gmd:CI_OnlineResource"]["gmd:linkage"]["gmd:URL"]
            name = item["gmd:fileIdentifier"]["gco:CharacterString"]
            name = name.split("/")[-1].split(".")[0]
            extend = item["gmd:identificationInfo"]["gmd:MD_DataIdentification"]["gmd:extent"]["gmd:EX_Extent"]
            spatial_extend = extend["gmd:geographicElement"]["gmd:EX_GeographicBoundingBox"]
            temporal_extend = extend["gmd:temporalElement"]["gmd:EX_TemporalExtent"]["gmd:extent"]["gml:TimePeriod"]

            response.append(
                Record(
                    name=name,
                    path=path,
                    spatial_extent=SpatialExtent(
                        top=spatial_extend["gmd:northBoundLatitude"]["gco:Decimal"],
                        bottom=spatial_extend["gmd:southBoundLatitude"]["gco:Decimal"],
                        left=spatial_extend["gmd:eastBoundLongitude"]["gco:Decimal"],
                        right=spatial_extend["gmd:westBoundLongitude"]["gco:Decimal"],
                        crs="EPSG:4326" 
                    ),
                    temporal_extent="{0}/{1}".format(temporal_extend["gml:beginPosition"], 
                                                     temporal_extend["gml:endPosition"])
                )
            )

        return response

    def get_file_paths(self, product: str, bbox: list, start: str, end: str) -> list:
        """Returns the file paths of the records of the specified products
        in the temporal and spatial extents.

        Arguments:
            product {str} -- The identifier of the product
            bbox {list} -- The spatial extent of the records
            start {str} -- The start date of the temporal extent
            end {str} -- The end date of the temporal extent

        Returns:
            list -- The records data
        """

        records=self._get_records(product, bbox, start, end)

        # TODO: Better solution than this bulls** xml paths
        response=[]
        for item in records:
            path=item["gmd:distributionInfo"]["gmd:MD_Distribution"]["gmd:transferOptions"][
                "gmd:MD_DigitalTransferOptions"]["gmd:onLine"][0]["gmd:CI_OnlineResource"]["gmd:linkage"]["gmd:URL"]
            name=path.split("/")[-1].split(".")[0]
            date=item["gmd:identificationInfo"]["gmd:MD_DataIdentification"]["gmd:extent"]["gmd:EX_Extent"][
                "gmd:temporalElement"]["gmd:EX_TemporalExtent"]["gmd:extent"]["gml:TimePeriod"]["gml:beginPosition"][0:10]

            response.append(
                FilePath(
                    date=date,
                    name=name,
                    path=path
                )
            )

        return response

    def _get_records(self, product: str=None, bbox: list=None, start: str=None, end: str=None, series: bool=False) -> list:
        """Parses the XML request for the CSW server and collects the responsed by the
        batch triggered _get_single_records function.

        Keyword Arguments:
            product {str} -- The identifier of the product (default: {None})
            bbox {list} -- The spatial extent of the records (default: {None})
            start {str} -- The end date of the temporal extent (default: {None})
            end {str} -- The end date of the temporal extent (default: {None})
            series {bool} -- Specifier if series (products) or records are queried (default: {False})

        Raises:
            CWSError -- If a problem occures while communicating with the CSW server

        Returns:
            list -- The records data
        """

        # Parse the XML request by injecting the query data into the XML templates
        output_schema='https://github.com/radiantearth/stac-spec'

        xml_filters=[]

        if series:
            xml_filters.append(xml_series)

        if product:
            if series:
                xml_filters.append(xml_product.format(
                    property="dc:identifier", product=product))
            else:
                xml_filters.append(xml_product.format(
                    property="apiso:ParentIdentifier", product=product))

        if start and not series:
            xml_filters.append(xml_begin.format(start=start))

        if end and not series:
            xml_filters.append(xml_end.format(end=end))

        if bbox and not series:
            xml_filters.append(xml_bbox.format(bbox=bbox))

        if len(xml_filters) == 0:
            return CWSError("Please provide fiters on the data (bounding box, start, end)")

        filter_parsed=""
        if len(xml_filters) == 1:
            filter_parsed=xml_filters[0]
        else:
            tmp_filter=""
            for xml_filter in xml_filters:
                tmp_filter += xml_filter
            filter_parsed=xml_and.format(children=tmp_filter)

        # While still data is available send requests to the CSW server (-1 if not more data is available)
        all_records=[]
        record_next=1

        # Create a request and cache the data for a day
        # Caching to increase speed
        path_to_cache = self._get_cache_path(product, series)
        if not self._check_cache(path_to_cache):
            while int(record_next) > 0:
                record_next, records=self._get_single_records(
                    record_next, filter_parsed, output_schema)
                all_records += records
            self._cache_json(all_records, path_to_cache)
        else:
            all_records = self._get_json_cache(path_to_cache)

        return all_records

    def _get_single_records(self, start_position: int, filter_parsed: dict, output_schema: str) -> list:
        """Sends a single request to the CSW server, requesting data about records or products.

        Arguments:
            start_position {int} -- The request start position
            filter_parsed {dict} -- The prepared XML template
            output_schema {str} -- The desired output schema of the response

        Raises:
            CWSError -- If a problem occures while communicating with the CSW server

        Returns:
            list -- The returned record or product data
        """

        # Parse the XML by injecting iteration dependend variables
        xml_request=xml_base.format(
            children=filter_parsed, output_schema=output_schema, start_position=start_position)
        response=post(self.csw_server_uri, data=xml_request)

        # Response error handling
        if not response.ok:
            print("Server Error {0}: {1}".format(
                response.status_code, response.text))
            raise CWSError("Error while communicating with CSW server.")

        if response.text.startswith("<?xml"):
            xml=parseString(response.text)
            print("{0}".format(xml.toprettyxml()))
            raise CWSError("Error while communicating with CSW server.")

        response_json=loads(response.text)

        if "ows:ExceptionReport" in response_json:
            print("{0}".format(dumps(response_json, indent=4, sort_keys=True)))
            raise CWSError("Error while communicating with CSW server.")

        # Get the response data
        search_result=response_json["csw:GetRecordsResponse"]["csw:SearchResults"]

        record_next=search_result["@nextRecord"]

        if "gmd:MD_Metadata" in search_result:
            records=search_result["gmd:MD_Metadata"]
        elif "csw:Record" in search_result:
            records=search_result["csw:Record"]
        elif "collection" in search_result:
            records=search_result["collection"]
        else:
            record_next=0
            records=[]

        if not isinstance(records, list):
            records=[records]

        return record_next, records

    def _cache_json(self, records: list, path_to_cache: str):
        """Stores the output to a json file with the id if single record or
        to a full collection json file

        Arguments:
            records {list} -- List of fetched records
            path_to_cache {str} -- The path to the cached file
        """

        if not records:
            return

        json_dump = dumps(records)
        with open(path_to_cache, 'w') as f:
            f.write(json_dump)

    def _check_cache(self, path_to_cache: str) -> bool:
        """Checks whether the cache exists and if it is older than a day from
        running this function

        Arguments:
            path_to_cache {str} -- The path to the cached file

        Returns:
            bool -- False if cache doesn't exist or hasn't refreshed for
            longer than a day, True otherwise
        """

        if path.isfile(path_to_cache):
            now = datetime.now()
            file_time = datetime.utcfromtimestamp(int(path.getmtime(path_to_cache)))
            difference = now - file_time
            if difference < timedelta(1):
                return True

        return False

    def _get_json_cache(self, path_to_cache: str) -> list:
        """Fetches the item(s) from the json cache

        Arguments:
            path_to_cache {str} -- The path to the cached file

        Returns:
            list -- List of dictionaries containing cached data
        """
        with open(path_to_cache, 'r') as f:
            data = loads(f.read())

        return data

    def _get_cache_path(self, product: str, series: bool) -> str:
        """Get the path of the cache depending on whether series or
        product were passed

        Arguments:
            product {str} -- The identifier of the product (default: {None})
            series {bool} -- Specifier if series (products) or records are queried (default: {False})


        Returns:
            str -- The path to the cached file
        """

        if series and not product:
            path_to_cache = path.join(self.cache_path, 'collections.json')
        else:
            path_to_cache = path.join(self.cache_path, product + '.json')

        return path_to_cache


class CSWSession(DependencyProvider):
    """The CSWSession is the DependencyProvider of the CSWHandler.
    """

    def get_dependency(self, worker_ctx: object) -> CSWHandler:
        """Return the instantiated object that is injected to a
        service worker

        Arguments:
            worker_ctx {object} -- The service worker

        Returns:
            CSWHandler -- The instantiated CSWHandler object
        """

        return CSWHandler(environ.get("CSW_SERVER"), environ.get("CACHE_PATH"))
