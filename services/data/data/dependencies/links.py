""" Module to create links for stac 0.6.2 compliance.
The values aren't currently in a db so the class LinkHandler handles creating them """

import os
from typing import Dict


class LinkHandler:
    def __init__(self, service_url: str) -> None:
        self.service_url = service_url
        self.api_endpoint = "collections"

    def _get_root_record(self) -> Dict[str, str]:
        rel = "root"
        href = os.path.join(self.service_url, self.api_endpoint)
        link = {"href": href, "rel": rel}
        return link

    def _get_parent_record(self) -> Dict[str, str]:
        rel = "parent"
        href = os.path.join(self.service_url, self.api_endpoint)
        link = {"href": href, "rel": rel}
        return link

    def _get_self_record(self, record: dict) -> Dict[str, str]:
        rel = "self"
        href = os.path.join(self.service_url, self.api_endpoint, record["id"])
        link = {"href": href, "rel": rel}
        return link

    def _get_self_collection(self) -> Dict[str, str]:
        rel = "self"
        href = os.path.join(self.service_url, self.api_endpoint)
        link = {"href": href, "rel": rel}
        return link

    def _get_source(self) -> None:
        pass

    def get_links(self, records: list = None, collection: bool = False) -> list:
        if not records:
            records = []
        if not collection:
            for record in records:
                links = [
                    self._get_self_record(record),
                    self._get_parent_record(),
                    self._get_root_record(),
                ]
                record.update({"links": links})
            return records
        else:
            links = [self._get_self_collection()]
            return links
