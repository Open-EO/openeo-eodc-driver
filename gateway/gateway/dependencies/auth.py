""" AuthenticationHandler """

from typing import Union, Optional, Callable, Tuple, Any, Dict

import requests
from dynaconf import settings
from flask import request
from flask.wrappers import Request, Response

from .response import ResponseParser, APIException


class AuthenticationHandler:
    """The AuthenticationHandler connects to the user service and verifies if the bearer token
    send by the user is valid.
    """

    def __init__(self, response_handler: ResponseParser):
        self._res = response_handler

    def validate_token(self, func: Callable, role: str, optional: bool = False) -> Union[Callable, Response]:
        """
        Decorator authenticate a user.

        Arguments:
            func {Callable} -- The wrapped function
            role {str} -- The required role to execute the function (user / admin)
            optional {bool} -- Flag for endpoints which may (not mast) accept a token

        Returns:
            Union[Callable, Response] -- Returns the decorator function or a HTTP error
        """
        def decorator(*args, **kwargs):
            try:
                token = self._parse_auth_header(request, optional=optional)
                if not token and optional:
                    return func()
                else:
                    user = self._verify_token(token, role)
                    return func(user=user)
            except Exception as exc:
                return self._res.error(exc)
        return decorator

    def _parse_auth_header(self, req: Request, optional: bool = False) -> Union[str, Exception]:
        """Parses and returns the bearer token. Raises an AuthenticationException if the Authorization
        header in the request is not correct.

        Arguments:
            req {Request} -- The Request object
            optional {bool} -- Flag for endpoints which may (not mast) accept a token

        Returns:
            Union[str, Exception] -- Returns the bearer token as string or raises an exception
        """

        if "Authorization" not in req.headers or not req.headers["Authorization"]:
            if optional:
                return
            else:
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

    def _verify_token(self, token: str, role: str) -> Dict[str, Any]:
        """
        Verify the supplied token either as basic or OIDC token.

        Arguments:
            token {str} -- The authentication token (basic / OIDC)
            role: {str} -- The required role to execute the function (user / admin)

        Raises:
            APIException -- If the token is not valid or the user does not have the required role or the token is not
                structured correctly.

        Returns:
            BaseUser -- The user object corresponding to the token
        """

        try:
            method, provider, token = token.split("/")
        except ValueError:
            raise APIException(
                msg="The token must be structured as following <authentication method>/<provider ID>/<token>!",
                code=401,
                service="gateway",
                internal=False)

        if method == "basic":
            user_entity = self._verify_basic_token(token)
        elif method == "oidc":
            user_entity = self._verify_oidc_token(token, provider)
        else:
            raise APIException(
                msg="The authentication method must be either 'basic' or 'oidc'",
                code=401,
                service="gateway",
                internal=False)

        if not role == "user":
            # If "admin" role is required and the user only has the "user" role this will through an exception
            self._check_user_role(user_entity, role=role)

        if not user_entity:
            raise APIException(
                msg="Invalid token. User could not be authenticated.",
                code=401,
                service="gateway",
                internal=False)
        return user_entity

    def _verify_basic_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verifies a basic token.

        Arguments:
            token {str} -- The basic authentication token

        Returns:
            Dict[str, Any] -- The user object corresponding to the token
        """
        from gateway.users.service import BasicAuthService
        return BasicAuthService(settings.SECRET_KEY).verify_auth_token(token)

    def _verify_oidc_token(self, token: str, provider: str) -> Optional[Dict[str, Any]]:
        """
        Verifies OIDC token.

        Arguments:
            token {str} -- The OIDC authentication token (currently an ID-token is required)
            provider {str} -- The used OIDC provider ID (must be supported by backend)

        Returns:
            Dict[str, Any] -- The user object corresponding to the token
        """
        from gateway.users.repository import get_user_entity_from_email

        # Get user from OIDC /userinfo endpoint
        user_entity = None
        id_flag, provider_wellknown = self._check_oidc_issuer_exists(provider)
        if id_flag:
            id_oidc_config = requests.get(provider_wellknown)
            userinfo_url = id_oidc_config.json()["userinfo_endpoint"]
            userinfo = requests.get(userinfo_url, headers={"Authorization": "Bearer " + token})
            if userinfo.status_code != 200:
                raise APIException(
                    msg="OIDC access token is invalid.",
                    code=401,
                    service="gateway",
                    internal=False,
                )
            user_entity = get_user_entity_from_email(userinfo.json()["email"])

        return user_entity

    def _check_user_role(self, user_entity: Dict[str, Any], role: str) -> bool:
        """
        Check user has the given role.

        Arguments:
            user_entity {Dict[str, Any]} -- The user object
            role {str} -- The required to role

        Raises:
            APIException -- If the user does not have the required role

        Returns:
            bool -- Whether the user has the required role
        """

        if not role == user_entity["role"]:
            raise APIException(
                msg=f"The user {user_entity} is not authorized to perform this operation.",
                code=403,
                service="gateway",
                internal=False)
        return True

    def _check_oidc_issuer_exists(self, id_openeo: str) -> Tuple[bool, str]:
        """
        Checks the given issuer_url exists in the database.

        Arguments:
            id_openeo {str} -- The id to check

        Raises:
            APIException -- If the issuer_url is not supported

        Returns:
            Tuple[bool, str] -- Whether the issuer_url is supported and its well-known url
        """

        from gateway.users.models import db, IdentityProviders
        identity_provider = db.session.query(IdentityProviders).filter(IdentityProviders.id_openeo == id_openeo).first()
        if not identity_provider:
            raise APIException(
                msg=f"The given Identity Provider '{id_openeo}' is not supported.",
                code=401,
                service="gateway",
                internal=False)
        return True, identity_provider.issuer_url + "/.well-known/openid-configuration"
