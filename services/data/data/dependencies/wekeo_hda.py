""" WEkEO Harmonized Data Access Session """


import logging
import requests
from time import sleep
from typing import Any, Dict, List

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
        self.service_headers = None
        self.set_headers()
        self.link_handler = LinkHandler(service_uri)

        LOGGER.debug("Initialized %s", self)
    
    def set_headers(self):
        response = requests.get(self.service_uri + "/gettoken",
                                auth=(self.service_user, self.service_password)
                                )
        if not response.ok:
            LOGGER.debug("Error while retrieving WEkEO API KEY.")
            raise HDAError(response.text)

        access_token = response.json()['access_token']
        self.service_headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
            }
    
    
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
        
        temp_var = data_id.split(':')
        wekeo_data_id = ':'.join(temp_var[:-1])
        response = requests.get(f"{self.service_uri}/querymetadata/{wekeo_data_id}",
                                headers=self.service_headers)
        if not response.ok:
            raise HDAError(response.text)

        data = response.json()
        data["id"] = data_id
        all_records = self.link_handler.get_links([data])
        all_records = add_non_csw_info([data])
        
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
        
        
        # bbox = {
        #     'west': 7.631289019431526,
        #     'east': 12.843490774792011,
        #     'north': 46.001682783839534,
        #     'south': 43.96918075703031
        # }
        # textent = ['2020-09-04T00:00:00.000Z', '2020-09-04T01:00:00.000Z']
        # var_id = data['parameters']['stringChoices'][1]['details']['valuesLabels'][temp_var[-1]]
        # self.get_filepaths(wekeo_data_id, var_id, bbox, textent)

        return collection
    
    def get_filepaths(self, wekeo_data_id: str, var_id: str, spatial_extent: Dict, temporal_extent: List) -> List[str]:
        """
        
        """
        
        # Create WEkEO 'data descriptor'
        data_descriptor = {
            "datasetId": wekeo_data_id,
            "boundingBoxValues": [
                {
                    "name": "bbox",
                    "bbox": [
                        spatial_extent["west"],
                        spatial_extent["south"],
                        spatial_extent["east"],
                        spatial_extent["north"]
                    ]
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
                    "value": var_id
                }
            ]
        }
        
        # Create a WEkEO 'datarequest'
        response = requests.post(f"{self.service_uri}/datarequest",
                                json=data_descriptor,
                                headers=self.service_headers)
        if not response.ok:
            raise HDAError(response.text)
        # check 'datarequest' status
        job_id = response.json()['jobId']
        while not response.json()['message']:
            response = requests.get(f"{self.service_uri}/datarequest/status/{job_id}",
                                    headers=self.service_headers)
            sleep(3)
        if not response.ok:
            raise HDAError(response.text)
        
        # Get job result -> list of files corresponding to the datarequest
        response = requests.get(f"{self.service_uri}/datarequest/jobs/{job_id}/result",
                                headers=self.service_headers)
        if not response.ok:
            raise HDAError(response.text)
        
        # Loop through list and download each file
        for item in response.json()['content']:
            # TODO use threads to do this async and in parallel
            
            # Create a WEkEO 'dataorder'
            data2 = {"jobId": job_id,"uri": item['url']}
            response2 = requests.post(f"{self.service_uri}/dataorder",json=data2,headers=self.service_headers)
            if not response2.ok:
                raise HDAError(response.text)
            # check 'dataorder' status
            order_id = response2.json()['orderId']
            while not response2.json()['message']:
                response2 = requests.get(f"{self.service_uri}/dataorder/status/{order_id}",
                                        headers=self.service_headers)
                sleep(3)
            
            # Download file
            response3 = requests.get(f"{self.service_uri}/dataorder/download/{order_id}",headers=self.service_headers, stream=True)
            with open('s3_test.zip', 'wb') as f:
                for chunk in response3.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        
        

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
