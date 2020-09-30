"""Manage user authentication."""
from enum import Enum
from typing import Any, Callable, Dict, Optional, Tuple, Union

import requests
from dynaconf import settings
from flask import request
from flask.wrappers import Request, Response

from .response import APIException, ResponseParser


class TokenAuthenticationRequirement(Enum):
    """Provides possible requirements for bearer token authentication to access an endpoint."""

    required = "required"
    """Access to this endpoint requires bearer token authentication."""
    optional = "optional"
    """This endpoint can be access without bearer token authentication, but more information may be available with."""
    prohibited = "prohibited"
    """This endpoint can not be accessed with bearer token authentication."""


class TokenAuthenticationHandler:
    """Authenticates users by validating a token.

    Attributes:
        response_handler: The ResponseParser to parse an exception if the authentication fails.
    """

    def __init__(self, response_handler: ResponseParser) -> None:
        """Initialize AuthenticationHandler."""
        self._res = response_handler

    def validate_token(self, func: Callable, role: str, required: bool = False) -> Callable:
        """Decorator to authenticate a user by validating its token.

        Args:
            func: The wrapped function which the user wants to execute.
            role: The required role to execute the function (e.g.: user / admin).
            required: Flag for endpoints which only accept authenitcated requests.

        Returns:
            The decorator function.
        """
        def decorator(*args: Any, **kwargs: Any) -> Union[Callable, Response]:
            """Validate a token and execute the provided function.

            The user object generated from the token is passed to the function as parameter 'user'.

            Returns:
                 The decorated function with the additional parameter user or a HTTP error
            """
            try:
                token = self._parse_auth_header(request, required=required)
                if not token:
                    if not required:
                        return func()
                    else:
                        raise APIException(
                            msg="Missing required Bearer token.",
                            code=401,
                            service="gateway",
                            internal=False)
                else:
                    user = self._verify_token(token, role)
                    return func(user=user)
            except Exception as exc:
                return self._res.error(exc)
        return decorator

    def _parse_auth_header(self, req: Request, required: bool = False) -> Optional[str]:
        """Parse an auth header and return the bearer token.

        Raises an AuthenticationException if the Authorization header in the request is not correct.

        Args:
            req: The Request object.
            required: Flag for endpoints only accept authenticated requests.

        Raises:
            :class:`~gateway.dependencies.AAPIException`: if there is no token or it is not a Bearer token.

        Returns:
            The bearer token as string.
        """
        if "Authorization" not in req.headers or not req.headers["Authorization"]:
            if required:
                raise APIException(
                    msg="Missing 'Authorization' header.",
                    code=401,
                    service="gateway",
                    internal=False)
            else:
                return None

        token_split = req.headers["Authorization"].split(" ")

        if len(token_split) != 2 or token_split[0] != "Bearer":
            raise APIException(
                msg="Invalid Bearer token.",
                code=401,
                service="gateway",
                internal=False)

        return token_split[1]

    def _verify_token(self, token: str, role: str) -> Dict[str, Any]:
        """Verify the supplied token either as basic or OIDC token.

        Args:
            token: The authentication token (basic / OIDC)
            role: The required role to execute the function (user / admin)

        Raises:
            :class:`~gateway.dependencies.AAPIException`: If the token is not valid or the user does not have the
                required role or the token is not structured correctly.

        Returns:
            The user dict corresponding to the token.
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

        if not user_entity:
            raise APIException(
                msg="Invalid token. User could not be authenticated.",
                code=401,
                service="gateway",
                internal=False)

        if not role == "user":
            # If "admin" role is required and the user only has the "user" role this will through an exception
            self._check_user_role(user_entity, role=role)

        return user_entity

    def _verify_basic_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a basic token.

        Args:
            token: The basic authentication token.

        Returns:
            The user object corresponding to the token or None if the token is invalid.
        """
        from gateway.users.service import BasicAuthService
        return BasicAuthService(settings.SECRET_KEY).verify_auth_token(token)

    def _verify_oidc_token(self, token: str, provider: str) -> Optional[Dict[str, Any]]:
        """Verify OIDC token.

        Args:
            token: The OIDC authentication token (of type access-token)
            provider: The used OIDC provider ID (must be supported by backend)

        Raises:
            :class:`~gateway.dependencies.AAPIException`: If the token is not valid.

        Returns:
            The user object corresponding to the token
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
        """Check user has the required role.

        Args:
            user_entity: The user object.
            role: The required to role.

        Raises:
            :class:`~gateway.dependencies.AAPIException`: If the user does not have the required role.

        Returns:
            True if the user has the required role.
        """
        if not role == user_entity["role"]:
            raise APIException(
                msg=f"The user {user_entity} is not authorized to perform this operation.",
                code=403,
                service="gateway",
                internal=False)
        return True

    def _check_oidc_issuer_exists(self, id_openeo: str) -> Tuple[bool, str]:
        """Check the given identity provider exists in the database.

        Args:
            id_openeo: The id to check.

        Raises:
            :class:`~gateway.dependencies.AAPIException`: If the issuer_url is not supported.

        Returns:
            True and the issuer's well-known url if the identity provider exists.
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
