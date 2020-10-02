""" WEkEO Harmonized Data Access Session """


import logging
from time import sleep
from typing import Dict, List, Tuple

import requests
from dynaconf import settings
from nameko.extensions import DependencyProvider

from .links import LinkHandler
from .stac_utils import add_non_csw_info
from ..models import Collection, Collections

LOGGER = logging.getLogger("standardlog")


class HDAError(Exception):
    """ HDAError raises if a error occurs while querying the WEkEO HDA API. """

    def __init__(self, msg: str = "") -> None:
        super(HDAError, self).__init__(msg)


class HDAHandler:
    """
    """

    def __init__(self, service_uri: str, service_user: str, service_password: str) -> None:
        self.service_uri = service_uri
        self.service_user = service_user
        self.service_password = service_password
        self.service_headers = {
            'Authorization': None,
            'Accept': 'application/json'
        }
        self._set_headers()
        self.link_handler = LinkHandler(service_uri)

        LOGGER.debug("Initialized %s", self)

    def _set_headers(self) -> None:
        response = requests.get(self.service_uri + "/gettoken",
                                auth=(self.service_user, self.service_password)
                                )
        if not response.ok:
            LOGGER.debug("Error while retrieving WEkEO API KEY.")
            raise HDAError(response.text)

        access_token = response.json()['access_token']
        self.service_headers['Authorization'] = f'Bearer {access_token}'

    def get_all_products(self) -> Collections:
        """Returns all products available at the back-end.

        Returns:
            list -- The list containing information about available products
        """

        collection_list = []
        for data_id in settings.WHITELIST_WEKEO:
            collection_list.append(self.get_product(data_id))

        links = self.link_handler.get_links(collection=True)
        collections = Collections(collections=collection_list, links=links)

        return collections

    def get_product(self, data_id: str) -> Collection:
        """Returns information about a specific product.

        Arguments:
            data_id {str} -- The identifier of the product

        Returns:
            dict -- The product data
        """

        # temp_var = data_id.split(':')
        # wekeo_data_id = ':'.join(temp_var[:-1])
        wekeo_data_id, _ = self._split_collection_id(data_id)
        response = requests.get(f"{self.service_uri}/querymetadata/{wekeo_data_id}",
                                headers=self.service_headers)
        if not response.ok:
            raise HDAError(response.text)

        data = response.json()
        data["id"] = data_id
        data = add_non_csw_info([data])
        data = self.link_handler.get_links(data)[0]

        collection = Collection(
            stac_version=data["stac_version"],
            id=data["id"],
            description=data["description"],
            license=data["userTerms"]["termsId"],
            extent=data["extent"],
            links=data["links"],
            title=data["title"],
            keywords=data["keywords"],
            cube_dimensions=data["cube:dimensions"],
            summaries=data["summaries"],
        )

        return collection

    def get_filepaths(self, collection_id: str, spatial_extent: Dict, temporal_extent: List) -> List[str]:
        """Retrieves a URL list from the WEkEO HDA according to the specified parameters.

        Arguments:
            collecion_id {str} -- identifier of the collection
            spatial_extent {List[float]} -- bounding box [ymin, xmin, ymax, ymax]
            temporal_extent {List[str]} -- e.g. ["2018-06-04", "2018-06-23"]

        Returns:
            list -- list of URLs / filepaths
        """

        # Create Data Descriptor
        data_descriptor = self.create_data_descriptor(collection_id, spatial_extent, temporal_extent)

        # Create a Data Request job
        job_id = self._create_datarequest(data_descriptor)

        # Get URLs for individual files
        filepaths, next_page_url = self._get_download_urls(f"{self.service_uri}/datarequest/jobs/{job_id}/result")
        while next_page_url:
            tmp_filepaths, next_page_url = self._get_download_urls(next_page_url)
            filepaths.extend(tmp_filepaths)

        return filepaths, job_id

    def _split_collection_id(self, collection_id: str) -> List:
        """Splits a collection_id into the collection name and variable name, e.g.
        EO:ESA:DAT:SENTINEL-5P:TROPOMI:L2__NO2___ into:
        EO:ESA:DAT:SENTINEL-5P:TROPOMI and L2__NO2___.

        Arguments:
            collecion_id {str} -- identifier of the collection

        Returns:
            list -- list with two strings
        """

        temp_var = collection_id.split(':')
        wekeo_data_id = ':'.join(temp_var[:-1])
        wekeo_var_id = temp_var[-1]

        return [wekeo_data_id, wekeo_var_id]

    def create_data_descriptor(self, collection_id: str, spatial_extent: Dict, temporal_extent: List) -> Dict:
        """ """

        wekeo_data_id, wekeo_var_id = self._split_collection_id(collection_id)

        # Create WEkEO 'data descriptor'
        data_descriptor = {
            "datasetId": wekeo_data_id,
            "boundingBoxValues": [
                {
                    "name": "bbox",
                    "bbox": spatial_extent
                }
            ],
            "dateRangeSelectValues": [
                {
                    "name": "position",
                    "start": temporal_extent[0],
                    "end": temporal_extent[1]
                }
            ],
            "stringChoiceValues": [
                {
                    "name": "processingLevel",
                    "value": "LEVEL2"
                },
                {
                    "name": "productType",
                    "value": wekeo_var_id
                }
            ]
        }

        return data_descriptor

    def _create_datarequest(self, data_descriptor: Dict) -> str:
        """ """

        # Create a WEkEO 'datarequest'
        response = requests.post(f"{self.service_uri}/datarequest",
                                 json=data_descriptor,
                                 headers=self.service_headers)
        if not response.ok:
            raise HDAError(response.text)
        # Check 'datarequest' status
        job_id = response.json()['jobId']
        while not response.json()['message']:
            response = requests.get(f"{self.service_uri}/datarequest/status/{job_id}",
                                    headers=self.service_headers)
            sleep(1)
        if not response.ok:
            raise HDAError(response.text)

        return job_id

    def _get_download_urls(self, url: str) -> Tuple:
        """ """

        response = requests.get(url, headers=self.service_headers)
        if not response.ok:
            raise HDAError(response.text)
        download_urls = []
        next_page_url = None
        if response.json()['content']:
            next_page_url = response.json()['nextPage']

            for item in response.json()['content']:
                download_urls.append(item['url'])

        return download_urls, next_page_url


class HDASession(DependencyProvider):
    """ The HDASession is the DependencyProvider of the HDAHandler. """
    def get_dependency(self, worker_ctx: object) -> HDAHandler:
        """Return the instantiated object that is injected to a
        service worker

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
