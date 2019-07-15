''' Module to create links for stac 0.6.2 compliance. 
The values aren't currently in a db so the class LinkHandler handles creating them '''

class LinkHandler:

    def __init__(self, service_url: str):
        self.service_url = service_url
        self.api_endpoint = 'collections'

    def _get_root(self):
        rel = 'root'
        href = self.service_url + self.api_endpoint
        root_link = {'href': href, 'rel': rel}
        return root_link

    def _get_parent(self):
        rel = 'parent'
        href = self.service_url + self.api_endpoint
        root_link = {'href': href, 'rel': rel}
        return root_link

    def _get_self(self, record):
        rel = 'self'
        href = self.service_url + self.api_endpoint + '/' + record['id']
        root_link = {'href': href, 'rel': rel}
        return root_link

    def _get_source(self):
        pass

    def get_links(self, records: list) -> list:
        for record in records:
            links = [self._get_self(record), self._get_parent(), self._get_root()]
            record.update({'links': links})
            
        return records
