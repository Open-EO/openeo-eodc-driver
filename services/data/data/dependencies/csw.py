"""Provides all functionalities to handle communication via CSW.

Next to the direct communication with the CSW server this also includes providing a nameko dependency to be used in the
data service.
"""

import ast
import logging
from json import dumps
from os import makedirs, path
from typing import List, Tuple

from defusedxml.minidom import parseString
from dynaconf import settings
from nameko.extensions import DependencyProvider
from owslib.csw import CatalogueServiceWeb
from owslib.fes import BBox, PropertyIsGreaterThan, PropertyIsLessThan, PropertyIsLike
from requests import post

from .cache import cache_json, get_cache_path, get_json_cache
from .links import LinkHandler
from .stac_utils import add_non_csw_info
from .xml_templates import xml_and, xml_base, xml_bbox, xml_begin, xml_end, xml_product, xml_series
from ..models import Collection, Collections, Extent, SpatialExtent, TemporalExtent

LOGGER = logging.getLogger("standardlog")


class CSWError(Exception):
    """CWSError raises if an error occurs while querying the CSW server."""

    def __init__(self, msg: str = "") -> None:
        """Initialise CSWError class."""
        super(CSWError, self).__init__(msg)


class CSWHandler:
    """Handles communication with the CSW server.

    This includes parsing a XML request, parsing the response and mapping the values to the
    required output format.

    Attributes:
        csw_server_uri: The URI the CSW server.
        data_access: The required data_access to access data from this CSW server.
        group_property: The query property to use when querying for a product.
        white_list: A list of collections available at the CSW server which should be exposed via OpenEO.
        cache_path: The path to a directory where records should be cached.
    """

    def __init__(self, csw_server_uri: str, data_access: str, group_property: str, white_list: List[str],
                 cache_path: str) -> None:
        """Initialise CSWHandler."""
        self.csw_server_uri = csw_server_uri
        self.data_access = data_access
        self.group_property = group_property
        self.white_list = white_list
        self.cache_path = cache_path
        self.link_handler = LinkHandler()

        self._create_path(self.cache_path)
        LOGGER.debug("Initialized %s", self)

    def __repr__(self) -> str:
        """Return a simple human readable representation of the CSWHandler."""
        return f"CSWHandler('{self.csw_server_uri}')"

    def _create_path(self, cur_path: str) -> None:
        """Create a directory structure."""
        if not path.isdir(cur_path):
            makedirs(cur_path)

    def get_all_products(self) -> Collections:
        """Return all products available at the backend.

        Returns:
            The list containing information about available products.
        """
        data = self._get_records(series=True)

        collection_list = []
        for collection in data:
            try:
                bbox = ast.literal_eval(collection["extent"]["spatial"]["bbox"])
                interval = ast.literal_eval(collection["extent"]["temporal"]["interval"])
            except TypeError:
                # TODO this "workaround" is needed for SIG0 data, remove when corresponding CSW server has been updated
                bbox = [[-180.0, -90.0, 180.0, 90.0]]
                interval = [None, None]

            # TODO find way to write to JSON with correct format
            collection_list.append(
                Collection(
                    stac_version=collection["stac_version"],
                    id_=collection["id"],
                    description=collection["description"],
                    license_=collection["license"],
                    extent=Extent(
                        spatial=SpatialExtent(bbox=bbox),
                        temporal=TemporalExtent(interval=interval)),
                    cube_dimensions=collection["cube:dimensions"],
                    summaries=collection["summaries"],
                    links=collection["links"],
                )
            )
        links = self.link_handler.get_links(collection=True)
        collections = Collections(collections=collection_list, links=links)

        return collections

    def get_product(self, data_id: str) -> Collection:
        """Return information about a specific product.

        Args:
            data_id: The identifier of the product.

        Returns:
            The product data as collection.
        """
        data = self._get_records(data_id, series=True)[0]
        try:
            # TODO find way to write to JSON with correct format
            data['extent']['spatial']['bbox'] = ast.literal_eval(data['extent']['spatial']['bbox'])
            data['extent']['temporal']['interval'] = ast.literal_eval(data['extent']['temporal']['interval'])
        except TypeError:
            # TODO this "workaround" is needed for SIG0 data, remove when corresponding CSW server has been updated
            data['extent']['spatial']['bbox'] = [[-180.0, -90.0, 180.0, 90.0]]
            data['extent']['temporal']['interval'] = [None, None]

        collection = Collection(
            stac_version=data["stac_version"],
            id_=data["id"],
            description=data["description"],
            license_=data["license"],
            extent=data["extent"],
            links=data["links"],
            title=data["title"],
            keywords=data["keywords"],
            cube_dimensions=data["cube:dimensions"],
            summaries=data["summaries"],
        )

        return collection

    def refresh_cache(self, use_cache: bool = False) -> None:
        """Refresh the product cache.

        Args:
            use_cache: Specifies whether to or not to refresh the cache.
                A bit redundant because submitted through an additional POST.
        """
        LOGGER.debug("Refreshing cache %s", use_cache)
        data = self._get_records(series=True, use_cache=use_cache)
        for collection in data:
            _ = self._get_records(
                collection["id"], series=True, use_cache=use_cache)[0]

    def _get_records(
            self,
            product: str = None,
            bbox: list = None,
            start: str = None,
            end: str = None,
            series: bool = False,
            use_cache: bool = True,
    ) -> list:
        """Parse the XML request for the CSW server and collects the response.

        The response is collected by the batch triggered _get_single_records function.

        Args:
            product: The identifier of the product.
            bbox: The spatial extent of the records.
            start: The start date of the temporal extent.
            end: The end date of the temporal extent.
            series: Specifier if series (products) or records are queried.
            use_cache: Specifies whether to use the cache.

        Raises:
            CSWError -- If a problem occurs while communicating with the CSW server or no filter is provided.

        Returns:
            The resulting records data.
        """
        LOGGER.debug(
            "_get_records() parameters: product: %s, bbox:%s, start:%s, end:%s, series:%s, use_cache:%s",
            product,
            bbox,
            start,
            end,
            series,
            use_cache,
        )
        all_records = []
        path_to_cache = get_cache_path(self.cache_path, product, series, self.data_access)
        # Caching to increase speed
        # Create a request and cache the data for a day
        if not use_cache:

            # Parse the XML request by injecting the query data into the XML templates
            output_schema = "https://github.com/radiantearth/stac-spec"
            cur_filter = self._get_csw_filter(
                product, bbox, start, end, series)

            # While still data is available send requests to the CSW server (-1 if not more data is available)
            record_next = 1
            while int(record_next) > 0:
                record_next, records = self._get_single_records(
                    record_next, cur_filter, output_schema
                )
                all_records += records
            # additionally add the links, cube:dimensions, summaries to each record and collection
            all_records = self.link_handler.get_links(all_records)
            all_records = add_non_csw_info(all_records)
            cache_json(all_records, path_to_cache)
        else:
            all_records = get_json_cache(path_to_cache)

        return all_records

    def _get_csw_filter(
            self,
            product: str = None,
            bbox: list = None,
            start: str = None,
            end: str = None,
            series: bool = False,
    ) -> str:
        """
        Create a CSW filter based on the given parameters.

        Args:
            product: The identifier of the product.
            bbox: The spatial extent of the records.
            start: The start date of the temporal extent.
            end: The end date of the temporal extent.
            series: Specifier if series (products) or records are queried.

        Raises:
            CWSError: If no filter is provided.

        Returns:
            CSW filter in string format.
        """
        xml_filters = []

        if series:
            xml_filters.append(xml_series)

        if product:
            if series:
                xml_filters.append(
                    xml_product.format(
                        property="dc:identifier", product=product)
                )
            else:
                xml_filters.append(
                    xml_product.format(
                        property=self.group_property, product=product
                    )
                )

        if start and not series:
            xml_filters.append(xml_begin.format(start=start))

        if end and not series:
            xml_filters.append(xml_end.format(end=end))

        if bbox and not series:
            xml_filters.append(xml_bbox.format(bbox=bbox))

        if len(xml_filters) == 0:
            raise CSWError(
                "Please provide filters on the data (e.g. product, bounding box, start, end)"
            )

        if len(xml_filters) == 1:
            filter_parsed = xml_filters[0]
        else:
            tmp_filter = "".join(xml_filters)
            filter_parsed = xml_and.format(children=tmp_filter)

        return filter_parsed

    def _get_single_records(
            self, start_position: int, filter_parsed: str, output_schema: str
    ) -> Tuple[int, list]:
        """Send a single request to the CSW server, requesting data about records or products.

        Args:
            start_position: The request start position.
            filter_parsed: The prepared XML template.
            output_schema: The desired output schema of the response.

        Raises:
            CWSError: If a problem occurs while communicating with the CSW server.

        Returns:
            A Tuple with the integer position of the next result and the returned record or product data.
        """
        # Parse the XML by injecting iteration depended variables
        xml_request = xml_base.format(
            children=filter_parsed,
            output_schema=output_schema,
            start_position=start_position,
        )
        LOGGER.debug("POST:\n%s", xml_request)
        response = post(self.csw_server_uri, data=xml_request)

        # Response error handling
        if not response.ok:
            LOGGER.error("Server Error %s: %s",
                         response.status_code, response.text)
            raise CSWError("Error while communicating with CSW server.")

        if response.text.startswith("<?xml"):
            xml = parseString(response.text)
            LOGGER.error("%s", xml.toprettyxml())
            raise CSWError("Error while communicating with CSW server.")

        response_json = response.json()

        if "ows:ExceptionReport" in response_json:
            LOGGER.error("%s", dumps(response_json, indent=4, sort_keys=True))
            raise CSWError("Error while communicating with CSW server.")

        # Get the response data
        search_result = response_json["csw:GetRecordsResponse"]["csw:SearchResults"]

        record_next = search_result["@nextRecord"]
        if "gmd:MD_Metadata" in search_result:
            records = search_result["gmd:MD_Metadata"]
        elif "csw:Record" in search_result:
            records = search_result["csw:Record"]
        elif "collection" in search_result:
            if isinstance(search_result["collection"], list):
                records = self.check_collections_id(search_result["collection"])
            else:
                records = search_result["collection"]
        else:
            records = []

        if not isinstance(records, list):
            records = [records]

        return record_next, records

    def check_collections_id(self, collections: List) -> List:
        """Return a list of collections from a CSW query, only if whitelisted.

        Args:
            collections: list of dicts (output of csw query with Series=True)

        Returns:
            All collection which are also whitelisted.
        """
        out_collections = []
        for collection in collections:
            if (collection['id'] in settings.WHITELIST) or (collection['id'] in settings.WHITELIST_DC):
                out_collections.append(collection)

        return out_collections

    def get_filepaths(self, collection_id: str, spatial_extent: List[float], temporal_extent: List[str]
                      ) -> List[str]:
        """Retrieve a file list from the a CSW server according to the specified parameters.

        Arguments:
            collecion_id {str} -- identifier of the collection
            spatial_extent {List[float]} -- bounding box [ymin, xmin, ymax, xmax]
            temporal_extent {List[str]} -- e.g. ["2018-06-04", "2018-06-23"]

        Returns:
            list -- list of filepaths
        """
        csw = CatalogueServiceWeb(self.csw_server_uri, timeout=300)

        constraints = []
        constraints.append(PropertyIsLike(self.group_property, collection_id))

        # Spatial filter
        constraints.append(BBox(spatial_extent))
        # Temporal filter
        constraints.append(PropertyIsGreaterThan('apiso:TempExtent_begin', temporal_extent[0]))
        constraints.append(PropertyIsLessThan('apiso:TempExtent_end', temporal_extent[1]))

        # Run the query
        csw.getrecords2(constraints=[constraints], maxrecords=100)

        # Put found records in a variable (dictionary)
        records0 = csw.records

        # Sort records
        records = []
        for record in records0:
            records.append(records0[record].references[0]['url'])
        records = sorted(records)

        return records


class CSWSession(DependencyProvider):
    """The CSWSession is the DependencyProvider of the CSWHandler."""

    def get_dependency(self, worker_ctx: object) -> CSWHandler:
        """Return the instantiated object that is injected to a service worker.

        Args:
            worker_ctx: The service worker.

        Returns:
            CSWHandler: The instantiated CSWHandler object.
        """
        return CSWHandler(
            csw_server_uri=settings.CSW_SERVER,
            data_access=settings.DATA_ACCESS,
            group_property=settings.GROUP_PROPERTY,
            white_list=settings.WHITELIST,
            cache_path=settings.CACHE_PATH,
        )


class CSWSessionDC(DependencyProvider):
    """The CSWSession is also the DependencyProvider of the CSWHandler.

    To provide two CSWHandler instances using a different configuration.
    """

    def get_dependency(self, worker_ctx: object) -> CSWHandler:
        """Return the instantiated object that is injected to a service worker.

        Args:
            worker_ctx: The service worker

        Returns:
            CSWHandler: The instantiated CSWHandler object
        """
        return CSWHandler(
            csw_server_uri=settings.CSW_SERVER_DC,
            data_access=settings.DATA_ACCESS_DC,
            group_property=settings.GROUP_PROPERTY_DC,
            white_list=settings.WHITELIST_DC,
            cache_path=settings.CACHE_PATH,
        )
