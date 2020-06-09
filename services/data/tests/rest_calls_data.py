import os

import requests


def test_collections() -> None:
    backend_url = "http://127.0.0.1:3000"
    basic_auth_url = backend_url + "/credentials/basic"
    collections_url = backend_url + "/collections"

    auth_response = requests.get(basic_auth_url, auth=(os.environ.get('USERNAME'), os.environ.get('PASSWORD')))
    auth_header = {'Authorization': 'Bearer basic//' + auth_response.json()['access_token']}

    response_get_all = requests.get(url=collections_url)
    assert response_get_all.ok
    response_post = requests.post(url=collections_url, headers=auth_header)
    assert response_post.ok
    response_get_all = requests.get(url=collections_url)
    assert response_get_all.ok
    response_get_single = requests.get(url=collections_url + "/s2a_prd_msil1c")
    assert response_get_single.ok


if __name__ == '__main__':
    test_collections()
