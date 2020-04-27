""" AuthenticationHandler """

from typing import Union, Optional, Callable

import jwt
import requests
from flask import request
from flask.wrappers import Request, Response

from .jwksutils import rsa_pem_from_jwk
from .response import ResponseParser, APIException


class AuthenticationHandler:
    """The AuthenticationHandler connects to the user service and verifies if the bearer token
    send by the user is valid.
    """

    def __init__(self, response_handler: ResponseParser):
        self._res = response_handler

    def validate_token(self, func: Callable, role: str) -> Union[Callable, Response]:
        """
        Decorator authenticate a user.

        Arguments:
            func {Callable} -- The wrapped function
            role {str} -- The required role to execute the function (user / admin)

        Returns:
            Union[Callable, Response] -- Returns the decorator function or a HTTP error
        """
        def decorator(*args, **kwargs):
            try:
                token = self._parse_auth_header(request)
                user_id = self._verify_token(token, role)
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
        """
        Verify the supplied token either as basic or OIDC token.

        Arguments:
            token {str} -- The authentication token (basic / OIDC)
            role: {str} -- The required role to execute the function (user / admin)

        Raises:
            APIException -- If the token is not valid or the user does not have the required role or the token is not
                structured correctly.

        Returns:
            str -- The user_id corresponding to the token
        """

        try:
            method, provider, token = token.split('/')
        except ValueError:
            raise APIException(
                msg="The token must be structured as following <authentication method>/<provider ID>/<token>!",
                code=401,
                service="gateway",
                internal=False)

        if method == 'basic':
            user_id = self._verify_basic_token(token)
        elif method == 'oidc':
            user_id = self._verify_oidc_token(token, provider)
        else:
            raise APIException(
                msg="The authentication method must be either 'basic' or 'oidc'",
                code=401,
                service="gateway",
                internal=False)

        if not role == 'user':
            if not self._check_user_role(user_id, role=role):
                user_id = None  # User does not have 'admin' role and is therefore not allowed to access the endpoint
                # NB this will cause an "invalid token" error, should be updated to specify that the user has no admin role

        if not user_id:
            raise APIException(
                msg='Invalid token. User could not be authenticated.',
                code=401,
                service="gateway",
                internal=False)
        return user_id

    def _verify_basic_token(self, token: str) -> Optional[str]:
        """
        Verifies a basic token.

        Arguments:
            token {str} -- The basic authentication token

        Returns:
            str -- The user_id corresponding to the token
        """
        from gateway.users.service import BasicAuthService
        return BasicAuthService().verify_auth_token(token)

    def _verify_oidc_token(self, token: str, provider: str) -> Optional[str]:
        """
        Verifies OIDC token.

        Arguments:
            token {str} -- The OIDC authentication token (currently an ID-token is required)
            provider {str} -- The used OIDC provider ID (must be supported by backend)

        Returns:
            str -- The user_id corresponding to the token
        """

        # Get user_id from OIDC /userinfo endpoint
        id_flag, provider_wellknown = self._check_oidc_issuer_exists(provider)
        if id_flag:
            id_oidc_config = requests.get(provider_wellknown)
            userinfo_url = id_oidc_config.json()['userinfo_endpoint']
            userinfo = requests.get(userinfo_url, headers={'Authorization': 'Bearer ' + token})
            user_id = self._get_user_id_from_email(userinfo.json()['email'])
        
        return user_id

    def _get_user_id_from_email(self, user_email: str) -> str:
        """
        Checks the email exists in the database and gets the corresponding user_id.

        Arguments:
            user_email {str} -- The user's email address

        Returns:
            str -- The user_id corresponding to the email
        """
        from gateway.users.models import db, Users

        user = db.session.query(Users).filter(Users.email == user_email).first()
        if not user:
            raise APIException(
                msg=f"The email address {user_email} does not exist in the database.",
                code=401,
                service="gateway",
                internal=False)
        return user.id

    def _check_user_role(self, user_id: str, role: str) -> bool:
        """
        Check user has the given role.

        Arguments:
            user_id {str} -- The user's id
            role {str} -- The required to role

        Raises:
            APIException -- If the user does not have the reuqired role

        Returns:
            bool -- Whether the user has the required role
        """

        from gateway.users.models import db, Users

        if not role == db.session.query(Users.role).filter(Users.id == user_id).scalar():
            raise APIException(
                msg=f"The user {user_id} is not authorized to perform this operation.",
                code=403,
                service="gateway",
                internal=False)
        return True

    def _check_oidc_issuer_exists(self, id_openeo: str) -> bool:
        """
        Checks the given issuer_url exists in the database.

        Arguments:
            id_openeo {str} -- The id to check

        Raises:
            APIException -- If the issuer_url is not supported

        Returns:
            str -- Whether the issuer_url is supported
        """
        
        from gateway.users.models import db, IdentityProviders
        identity_provider = db.session.query(IdentityProviders).filter(IdentityProviders.id_openeo == id_openeo).first()
        if not identity_provider:
            raise APIException(
                msg=f"The given Identity Provider '{id_openeo}' is not supported.",
                code=401,
                service="gateway",
                internal=False)
        return True, identity_provider.issuer_url + '/.well-known/openid-configuration'
