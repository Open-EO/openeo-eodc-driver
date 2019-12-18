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

    def validate_token(self, func, role):
        def decorator(*args, **kwargs):
            try:
                token = self._parse_auth_header(request)
                user_id, verified, authorized = self._verify_token(token, role)
                if user_id and verified and authorized:
                    return func(user_id=user_id)
            except Exception as exc:
                return self._res.error(exc)
        return decorator


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


    def _verify_token(self, token: str, role: str) -> str:
        
        def basic_token(token):
            """
            
            """
            
            from gateway.users.repository import verify_auth_token
            
            return verify_auth_token(token)
            
        def oidc_token(token):
            """
            
            """

            token_verified = None
            token_header = jwt.get_unverified_header(token)
            token_unverified = jwt.decode(token, verify=False)
            user_verified, user_id = self._verify_user(token_unverified['email'])
            issuer_verified = self._verify_oidc_issuer(token_unverified['iss']) # + "/.well-known/openid-configuration")

            if user_verified and issuer_verified:
                jwks = self._get_auth_jwks(token_unverified['iss'] + "/.well-known/openid-configuration")

                for key in jwks['keys']:
                    if key['kid'] == token_header['kid']:
                        public_key = rsa_pem_from_jwk(key)

                token_verified = jwt.decode(token,
                                            public_key,
                                            verify=True,
                                            algorithms=token_header['alg'],
                                            audience=token_unverified['azp'],
                                            issuer=token_unverified['iss'])
            if token_verified and user_id:
                return user_id, user_verified
            else:
                return None
            
        # TODO from version > 0.4.2 the token will contain basic or oidc and no "brute force" approach will be needed
        user_id, user_verified = basic_token(token)
        if not user_id:
            user_id, user_verified = oidc_token(token)
        user_authorized = self._verify_user_role(user_id, role=role)
        
        return user_id, user_verified, user_authorized


    def _verify_user(self, user_email: str) -> str:
        """

        """
        
        from gateway.users.models import db, Users
        
        user_id = None
        verify_flag = user_email == db.session.query(Users.email).filter(Users.email == user_email).scalar()
        if verify_flag:
            user_id = db.session.query(Users.id).filter(Users.email == user_email).scalar()
        else:
            raise APIException(
                msg="The email address of user {0} is not verified by the Identity Provider."\
                    .format(user_id),
                code=401,
                service="gateway",
                internal=False)
        
        return verify_flag, user_id
        

    def _verify_user_role(self, user_id: str, role: str) -> bool:
        """
        
        """
        
        from gateway.users.models import db, Users
        
        user_authorized = role == db.session.query(Users.role).filter(Users.id == user_id).scalar()
        
        if not user_authorized:
            raise APIException(
            msg="The user {0} is not authorized."\
                .format(user_id),
            code=403,
            service="gateway",
            internal=False)
        else:
            return user_authorized



    def _verify_oidc_issuer(self, issuer: str) -> bool:
        """

        """
        
        from gateway.users.models import db, IdentityProviders
        
        return issuer == db.session.query(IdentityProviders.issuer_url).filter(IdentityProviders.issuer_url == issuer).scalar()


    def _get_auth_jwks(self, oidc_well_known_url: str) -> dict:
        
        jwks = None    
        response = requests.get(oidc_well_known_url)
        if response.status_code == 200:
            jwks_uri = response.json()['jwks_uri']
            response = requests.get(jwks_uri)
            if response.status_code == 200:
                jwks = response.json()
        
        return jwks
