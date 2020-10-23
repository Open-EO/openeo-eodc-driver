"""WEkEO Harmonized Data Access Session."""


import logging
from typing import Any, Dict, List, Optional, Tuple

from dynaconf import settings
from eodc_openeo_bindings.wekeo_utils import get_collection_metadata, get_filepaths
from nameko.extensions import DependencyProvider

from .cache import cache_json, get_cache_path, get_json_cache
from .links import LinkHandler
from .stac_utils import add_non_csw_info
from ..models import Collection, Collections

LOGGER = logging.getLogger("standardlog")


class HDAError(Exception):
    """HDAError raises if an error occurs while querying the WEkEO HDA API."""

    def __init__(self, msg: str = "") -> None:
        """Initialise HDAError class."""
        super(HDAError, self).__init__(msg)


class HDAHandler:
    """Handles communication with WEkEO's Harmonized Data Access API."""

    def __init__(self, service_uri: str, service_user: str, service_password: str) -> None:
        """Initialise HDAHandler."""
        self.service_uri = service_uri
        self.service_user = service_user
        self.service_password = service_password
        self.link_handler = LinkHandler()

        LOGGER.debug("Initialized %s", self)

    def get_all_products(self, use_cache: bool = True) -> Collections:
        """Return all products available at the back-end.

        Returns:
            list -- The list containing information about available products
        """
        collection_list = []
        for data_id in settings.WHITELIST_WEKEO:
            col = self.get_product(data_id, use_cache=use_cache)
            if col:
                collection_list.append(col)

        links = self.link_handler.get_links(collection=True)
        collections = Collections(collections=collection_list, links=links)

        return collections

    def get_product(self, data_id: str, use_cache: bool = True) -> Optional[Collection]:
        """Return information about a specific product.

        Arguments:
            data_id {str} -- The identifier of the product

        Returns:
            dict -- The product data
        """
        path_to_cache = get_cache_path(settings.CACHE_PATH, data_id, False, settings.DATA_ACCESS_WEKEO)
        data: Dict[str, Any] = {}
        if use_cache:
            datasets = get_json_cache(path_to_cache)
            if len(datasets) == 1:
                data = datasets[0]
        else:
            wekeo_data_id, _ = self._split_collection_id(data_id)
            response = get_collection_metadata(self.service_uri, self.service_user, self.service_password,
                                               wekeo_data_id)

            dataset_wekeo = response.json()
            dataset_wekeo["id"] = data_id
            datasets_with_static_info: List[Dict[str, Any]] = add_non_csw_info([dataset_wekeo])
            datasets_with_static_info = self.link_handler.get_links(datasets_with_static_info)
            cache_json(datasets_with_static_info, path_to_cache)
            data = datasets_with_static_info[0]

        if data:
            return Collection(
                stac_version=data["stac_version"],
                id_=data["id"],
                description=data["description"],
                license_=data["userTerms"]["termsId"],
                extent=data["extent"],
                links=data["links"],
                title=data["title"],
                keywords=data["keywords"],
                cube_dimensions=data["cube:dimensions"],
                summaries=data["summaries"],
            )
        return None

    def refresh_cache(self, use_cache: bool = False) -> None:
        """Refresh the product cache.

        Args:
            use_cache: Specifies whether to or not to refresh the cache.
                A bit redundant because submitted through an additional POST.
        """
        LOGGER.debug("Refreshing cache %s", use_cache)
        _ = self.get_all_products(use_cache=use_cache)

    def get_filepaths(self, collection_id: str, spatial_extent: Dict, temporal_extent: List) -> Tuple[List, str]:
        """Retrieve a URL list from the WEkEO HDA according to the specified parameters.

        Arguments:
            collecion_id {str} -- identifier of the collection
            spatial_extent {List[float]} -- bounding box [ymin, xmin, ymax, xmax]
            temporal_extent {List[str]} -- e.g. ["2018-06-04", "2018-06-23"]

        Returns:
            list -- list of URLs / filepaths
        """
        # Create Data Descriptor
        wekeo_data_id, wekeo_var_id = self._split_collection_id(collection_id)
        filepaths, job_id = get_filepaths(self.service_uri, self.service_user, self.service_password,
                                          wekeo_data_id, wekeo_var_id, spatial_extent, temporal_extent)

        return filepaths, job_id

    def _split_collection_id(self, collection_id: str) -> List:
        """Separate collection and variable id.

        Splits a collection_id into the collection name and variable name,
        e.g. 'EO:ESA:DAT:SENTINEL-5P:TROPOMI:L2__NO2___' into:
        'EO:ESA:DAT:SENTINEL-5P:TROPOMI' and 'L2__NO2___'.

        Arguments:
            collecion_id {str} -- identifier of the collection

        Returns:
            list -- list with two strings
        """
        temp_var = collection_id.split(':')
        wekeo_data_id = ':'.join(temp_var[:-1])
        wekeo_var_id = temp_var[-1]

        return [wekeo_data_id, wekeo_var_id]


class HDASession(DependencyProvider):
    """The HDASession is the DependencyProvider of the HDAHandler."""

    def get_dependency(self, worker_ctx: object) -> HDAHandler:
        """Return the instantiated object that is injected to a service worker.

        Arguments:
            worker_ctx {object} -- The service worker

        Returns:
            HDAHandler -- The instantiated HDAHandler object
        """
        return HDAHandler(
            service_uri=settings.WEKEO_API_URL,
            service_user=settings.WEKEO_USER,
            service_password=settings.WEKEO_PASSWORD
        )
