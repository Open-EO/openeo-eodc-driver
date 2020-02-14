""" Module to create links for stac 0.6.2 compliance.
The values aren't currently in a db so the class LinkHandler handles creating them """


class LinkHandler:

    def __init__(self, service_url: str):
        self.service_url = service_url
        self.api_endpoint = 'collections'

    def _get_root_record(self):
        rel = 'root'
        href = self.service_url + self.api_endpoint
        link = {'href': href, 'rel': rel}
        return link

    def _get_parent_record(self):
        rel = 'parent'
        href = self.service_url + self.api_endpoint
        link = {'href': href, 'rel': rel}
        return link

    def _get_self_record(self, record):
        rel = 'self'
        href = self.service_url + self.api_endpoint + '/' + record['id']
        link = {'href': href, 'rel': rel}
        return link

    def _get_self_collection(self):
        rel = 'self'
        href = self.service_url + '/' + self.api_endpoint
        link = {'href': href, 'rel': rel}
        return link
    
    def _get_source(self):
        pass

    def get_links(self, records: list = None, collection: bool = False) -> list:
        if not records:
            records = []
        if not collection:
            for record in records:
                links = [self._get_self_record(record), self._get_parent_record(), self._get_root_record()]
                record.update({'links': links})
            return records
        else:
            links = [self._get_self_collection()]
            return links
