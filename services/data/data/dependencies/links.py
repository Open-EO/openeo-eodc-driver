"""Module to create links for stac 0.6.2 compliance.

The values aren't currently in a db so the class LinkHandler handles creating them.
"""

import os
from typing import List

from data.models import Link


class LinkHandler:
    """Handles creating links the OpenEO collection endpoint.

    Attributes:
        service_url: The URI reachable from the outside. This is the gateway url in the current setup.
    """

    def __init__(self, service_url: str) -> None:
        """Initialise LinkHandler."""
        self.service_url = service_url
        self.api_endpoint = "collections"

    def _get_root_record(self) -> Link:
        """Create /collections link with rel root."""
        rel = "root"
        href = os.path.join(self.service_url, self.api_endpoint)
        return Link(href=href, rel=rel)

    def _get_parent_record(self) -> Link:
        """Create /collections link with rel parent."""
        rel = "parent"
        href = os.path.join(self.service_url, self.api_endpoint)
        return Link(href=href, rel=rel)

    def _get_self_record(self, record: dict) -> Link:
        """Create link to specific product collection."""
        rel = "self"
        href = os.path.join(self.service_url, self.api_endpoint, record["id"])
        return Link(href=href, rel=rel)

    def _get_self_collection(self) -> Link:
        """Create /collection link with rel self."""
        rel = "self"
        href = os.path.join(self.service_url, self.api_endpoint)
        return Link(href=href, rel=rel)

    def _get_source(self) -> None:
        """Not implemented."""
        pass

    def get_links(self, records: list = None, collection: bool = False) -> List[dict]:
        """Build and return links for a specific product or the general collection.

        Args:
            records: List of records which are relevant.
            collection: Boolean flag whether to create link for the general collections summary.

        Returns:
            A list of dictionaries containing related links.
        """
        if not records:
            records = []
        if not collection:
            for record in records:
                links = [
                    self._get_self_record(record).to_dict(),
                    self._get_parent_record().to_dict(),
                    self._get_root_record().to_dict(),
                ]
                record.update({"links": links})
            return records
        else:
            links = [self._get_self_collection().to_dict()]
            return links
