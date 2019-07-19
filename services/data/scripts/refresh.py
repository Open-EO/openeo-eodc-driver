''' Run periodically with a cron job to refresh the cache '''

import os
import json
import pprint
from urllib.request import urlopen

if os.environ.get('SERVICE_URI'):
    SERVICE_URI = os.environ.get('SERVICE_URI') + 'collections'
else:
    SERVICE_URI = 'http://localhost:3000/collections'

def refresh_data():
    with urlopen(SERVICE_URI) as response:
        response_content = response.read()
        collections_dict = json.loads(response_content)
        if response.reason != 'OK':
            pprint.pprint(collections_dict)
            raise Exception('Exception raised by server with code {}.'.format(response.status))
        print('Refreshed collections')

    for record in collections_dict:
        for link in record['links']:
            if link['rel'] == 'self':
                refresh_link = link['href']
                with urlopen(refresh_link) as response:
                    record_dict = json.loads(response.read())
                    if response.reason != 'OK':
                        pprint.pprint(record_dict)
                        raise Exception('Exception raised by server with code {}.'.format(response.status))
        print('Refreshed', record['id'])

if __name__ == '__main__':
    refresh_data()
