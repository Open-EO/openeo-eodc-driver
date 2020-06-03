import requests

backend_url = "http://127.0.0.1:3000"


def get_auth(username: str = None, password: str = None):
    username = username if username else 'awesome_user'
    password = password if password else 'my-awesome-password'
    auth_response = requests.get(backend_url + "/credentials/basic", auth=(username, password))
    headers = {'Authorization': 'Bearer basic//' + auth_response.json()['access_token']}
    auth_response = requests.get(backend_url + "/me", headers=headers)
    print(auth_response.text)
    return headers


def check_oidc():
    oidc_url = backend_url + '/credentials/oidc'
    response = requests.get(oidc_url)
    print(response.text)


def check_add_identity_provider():

    idp_url = backend_url + '/users_mng/oidc_providers'
    id_json = {
        "id": "google1",
        "issuer": "https://accounts.google.com",
        "scopes": ["openid", "email"],
        "title": "Google1",
        "description": "Identity Provider supported for non-EODC users."
    }
    response = requests.post(idp_url, json=id_json, headers=get_auth())
    print(response.status_code)
    response = requests.delete(idp_url, json={'id': 'google1'}, headers=get_auth())
    print(response.status_code)


def check_add_user():
    user_dict = {
        "username": "your-name",
        "password": "your-password",
        "profile": "eodc_external",
        "budget": 100.45,
        "storage": {
            "free": 123,
            "quota": 123
        },
        "links": [
            {
                "rel": "latest-version",
                "href": "https://open-eo.github.io/openeo-api/#operation/describe-custom-process",
                "type": "the type of this link",
                "title": "the title of this link"
            },
            {
                "rel": "latest-version2",
                "href": "https://open-eo.github.io/openeo-api/#tag/Capabilities",
                "type": "the type of this link2",
                "title": "the title of this link2"
            }
        ]
    }
    response = requests.post(backend_url + '/users_mng/users', json=user_dict, headers=get_auth())
    print(response.status_code)
    response = requests.delete(backend_url + '/users_mng/users', json={"username": "your-name"}, headers=get_auth())
    print(response.status_code)


def check_me():
    response = requests.get(backend_url + '/me', headers=get_auth('your-name', 'your-password'))
    print(response.status_code)


def check_add_profile():
    profile_dict = {
        "name": "profile-x",
        "data_access": "basic,level-2"
    }
    response = requests.post(backend_url + '/users_mng/user_profiles', json=profile_dict, headers=get_auth())
    print(response.status_code)
    response = requests.delete(backend_url + '/users_mng/user_profiles', json={'name': 'profile-x'}, headers=get_auth())
    print(response.status_code)


if __name__ == '__main__':
    check_add_profile()
