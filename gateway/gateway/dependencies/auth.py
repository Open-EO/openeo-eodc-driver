""" AuthenticationHandler """


import os
from flask import request
from flask.wrappers import Request, Response
import jwt
import json
import requests
from typing import Union
from .jwksutils import rsa_pem_from_jwk
from .response import ResponseParser, APIException


class AuthenticationHandler:
    """The AuthenticationHandler connects to the user service and verifies if the bearer token
    send by the user is valid.
    """

    def __init__(self, response_handler: ResponseParser):
        self._res = response_handler

    def validate_token(self, func):
        def decorator(*args, **kwargs):
            try:
                token = self._parse_auth_header(request)
                user_id = verify_token(token)
                if user_id:
                    decorated_function = func(user_id=user_id)
                    return decorated_function
                else:
                    raise APIException(
                        msg="The email address of user {0} is not verified by the identity provider."\
                            .format(user_id),
                        code=401,
                        service="gateway",
                        internal=False)
            except Exception as exc:
                return self._res.error(exc)
        return decorator

    def check_role(self, f, role):
        def decorator(user_id=None):
            try:
                token = self._parse_auth_header(request)
                roles = self._get_roles(token)

                if role not in roles:
                    raise APIException(
                        msg="The user {0} is not authorized to access this resources."\
                            .format(user_id),
                        code=403,
                        service="gateway",
                        internal=False)

                return f(user_id=user_id)
            except Exception as exc:
                return self._res.error(exc)
        return decorator

    def _get_roles(self, token):
        roles = []
        if token:
            token_decode = decode(token, algorithms=['HS256'], verify=False)
            roles = token_decode["resource_access"]["openeo"]["roles"]
        return roles

    def _parse_auth_header(self, req: Request) -> Union[str, Exception]:
        """Parses and returns the bearer token. Raises an AuthenticationException if the Authorization
        header in the request is not correct.

        Arguments:
            req {Request} -- The Request object

        Returns:
            Union[str, Exception] -- Returns the bearer token as string or raises an exception
        """

        if "Authorization" not in req.headers or not req.headers["Authorization"]:
            raise APIException(
                msg="Missing 'Authorization' header.",
                code=401,
                service="gateway",
                internal=False)

        token_split = req.headers["Authorization"].split(" ")

        if len(token_split) != 2 or token_split[0] != "Bearer":
            raise APIException(
                msg="Invalid Bearer token.",
                code=401,
                service="gateway",
                internal=False)

        return token_split[1]


def verify_token(token):
    from gateway.users.repository import verify_auth_token
    token_verified = None
    token_header = jwt.get_unverified_header(token)
    token_unverified = jwt.decode(token, verify=False)
    user_id = verify_auth_token(token)

    if user_id:
        return user_id
    else:
        user_verified = verify_user(token_unverified['email'])
        issuer_verified = verify_oidc_issuer(token_unverified['iss'] + "/.well-known/openid-configuration")

        if user_verified and issuer_verified:
            jwks = get_auth_jwks(token_unverified['iss'] + "/.well-known/openid-configuration")

            for key in jwks['keys']:
                if key['kid'] == token_header['kid']:
                    public_key = rsa_pem_from_jwk(key)

            token_verified = jwt.decode(token,
                                        public_key,
                                        verify=True,
                                        algorithms=token_header['alg'],
                                        audience=token_unverified['azp'],
                                        issuer=token_unverified['iss'])

        user_id = token_verified['sub']
        if token_verified['email_verified']:
            return user_id
        else:
            return None


def verify_user(user_email):
    """

    """

    # NB this info should be stored in a database
    user_verified = False
    if user_email.split('@')[-1] == 'eodc.eu':
        user_verified = True
    else:
        with open(os.path.join(os.environ.get('OIDC_DIR'), 'users_external.json'), 'r') as f:
            users_list = json.load(f)
            if user_email in users_list['users']:
                user_verified = True

    return user_verified


def verify_oidc_issuer(issuer):
    """

    """

    # NB this info should be stored in a database
    issuer_verified = False
    if issuer in os.environ.get("OPENID_DISCOVERY"):
        issuer_verified = True
    else:
        # NB this info should be stored in a database
        with open(os.path.join(os.environ.get('OIDC_DIR'), 'issuers_external.json'), 'r') as f:
            oidc_list = json.load(f)
            if issuer in oidc_list['issuers']:
                issuer_verified = True

    return issuer_verified

def get_auth_jwks(oidc_well_known_url):
    
    jwks = None    
    response = requests.get(oidc_well_known_url)
    if response.status_code == 200:
        jwks_uri = response.json()['jwks_uri']
        response = requests.get(jwks_uri)
        if response.status_code == 200:
            jwks = response.json()
    
    return jwks
