""" Module to create links for stac 0.6.2 compliance.
The values aren't currently in a db so the class LinkHandler handles creating them """

import os
from typing import List

from data.models import Link


class LinkHandler:
    def __init__(self, service_url: str) -> None:
        self.service_url = service_url
        self.api_endpoint = "collections"

    def _get_root_record(self) -> Link:
        rel = "root"
        href = os.path.join(self.service_url, self.api_endpoint)
        return Link(href=href, rel=rel)

    def _get_parent_record(self) -> Link:
        rel = "parent"
        href = os.path.join(self.service_url, self.api_endpoint)
        return Link(href=href, rel=rel)

    def _get_self_record(self, record: dict) -> Link:
        rel = "self"
        href = os.path.join(self.service_url, self.api_endpoint, record["id"])
        return Link(href=href, rel=rel)

    def _get_self_collection(self) -> Link:
        rel = "self"
        href = os.path.join(self.service_url, self.api_endpoint)
        return Link(href=href, rel=rel)

    def _get_source(self) -> None:
        pass

    def get_links(self, records: list = None, collection: bool = False) -> List[Link]:
        if not records:
            records = []
        if not collection:
            for record in records:
                links = [
                    self._get_self_record(record),
                    self._get_parent_record(),
                    self._get_root_record(),
                ]
                record.extent(links)
            return records
        else:
            links = [self._get_self_collection()]
            return links
