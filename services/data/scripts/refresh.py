''' Run periodically with a cron job to refresh the cache '''

import os
import requests

if os.environ.get('DNS_URL'):
    SERVICE_URI = os.environ.get('DNS_URL') + '/collections'
else:
    SERVICE_URI = 'http://127.0.0.1:3000/collections'

def refresh_data():

    token = get_oidc_id_token(
        os.environ.get("OIDC_USERNAME"),
        os.environ.get("OIDC_PASSWORD"),
        os.environ.get("OIDC_CLIENT_ID"),
        os.environ.get("OIDC_REALM"),
        os.environ.get("OIDC_URL"),
        os.environ.get("OIDC_CLIENT_SECRET")
    )

    data = {'use_cache': False}
    auth_header = {'Authorization': 'Bearer ' + token['access_token']}

    res = requests.post(SERVICE_URI, data, headers=auth_header)

    if not res.ok:
        print('Couldn\'t cache data. {} - {}'.format(res.status_code, res.reason))
        return
    print('Cached the data!')
    return 1


def get_oidc_id_token(username, password, client_id, realm, url, client_secret=None):
    "Use requests"
    token_endpoint = os.path.join(url, "realms", realm, "protocol/openid-connect/token")
    postdata = {'username' : username,
                'password': password,
                'client_id': client_id,
                'grant_type': 'password'}
    if client_secret:
        postdata['client_secret'] = client_secret

    res = requests.post(token_endpoint, postdata)
    if not res.ok:
        print('Couldn\'t fetch token. {} - {}'.format(res.status_code, res.reason))
        return
    return res.json()

if __name__ == '__main__':
    refresh_data()
