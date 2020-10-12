"""Manage user authentication."""
import base64
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, Dict, Optional, Union

from flask import request
from flask.wrappers import Request, Response
from flask_nameko import FlaskPooledClusterRpcProxy
from passlib.apps import custom_app_context as pwd_context

from .response import APIException, ResponseParser
from .token_handler import BasicTokenHandler, OidcTokenHandler


class AuthRequirement(Enum):
    """Provides possible authentication requirements to access an endpoint."""

    token_required = "token_required"  # noqa S105
    """Access to this endpoint requires bearer token authentication."""
    token_optional = "token_optional"  # noqa S105
    """This endpoint can be access without bearer token authentication, but more information may be available with."""
    password_required = "password_required"  # noqa S105
    """Access to this endpoint requires basic authentication with a password."""
    password_optional = "password_optional"  # noqa S105
    """This endpoint can be access without basic authentication, but more information may be available with.

    Currently there is no endpoint using this option!
    """


class BaseAuthenticator(ABC):
    """Authenticate a user.

    Attributes:
        rpc: Connection to RPC functions - used to connect to the user service.
        response_handler: The ResponseParser to parse an exception if the authentication fails.
        **kwargs: Auxiliary arguments to be used by child classes.
    """

    def __init__(self, rpc: FlaskPooledClusterRpcProxy, response_handler: ResponseParser, **kwargs: Any) -> None:
        """Initialize AuthenticationHandler."""
        self._rpc = rpc
        self._res = response_handler

    @abstractmethod
    def validate(self, func: Callable, role: str, required: bool = False) -> Callable:
        """Decorator to authenticate a user.

        Args:
            func: The wrapped function which the user wants to execute.
            role: The required role to execute the function (e.g.: user / admin).
            required: Flag for endpoints which only accept authenticated requests.

        Returns:
            The decorator function.
        """
        pass

    def _parse_auth_header(self, req: Request, required: bool = False) -> Optional[str]:
        """Parse and return an auth header.

        Raises an AuthenticationException if the Authorization header in the request is not correct.

        Args:
            req: The Request object.
            required: Flag for endpoints only accept authenticated requests.

        Raises:
            :class:`~gateway.dependencies.APIException`: if there is no token or it is not a Bearer token.

        Returns:
            The authorization header.
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
        return req.headers["Authorization"]

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


class TokenAuthenticator(BaseAuthenticator):
    """Authenticate a user by validating a token.

    Attributes:
        rpc: Connection to RPC functions - used to connect to the user service.
        response_handler: The ResponseParser to parse an exception if the authentication fails.
        **kwargs: Auxiliary arguments to be used by child classes - not needed here.
    """

    def __init__(self, rpc: FlaskPooledClusterRpcProxy, response_handler: ResponseParser, **kwargs: Any) -> None:
        """Initialize TokenAuthenticator."""
        super(TokenAuthenticator, self).__init__(rpc, response_handler, **kwargs)
        self.basic_token_handler = BasicTokenHandler(self._rpc)
        self.oidc_token_handler = OidcTokenHandler(self._rpc)

    def validate(self, func: Callable, role: str, required: bool = False) -> Callable:
        """Decorator to authenticate a user by validating its token.

        Args:
            func: The wrapped function which the user wants to execute.
            role: The required role to execute the function (e.g.: user / admin).
            required: Flag for endpoints which only accept authenticated requests.

        Returns:
            The decorator function.
        """
        def token_decorator(*args: Any, **kwargs: Any) -> Union[Callable, Response]:
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
        return token_decorator

    def _parse_auth_header(self, req: Request, required: bool = False) -> Optional[str]:
        """Parse an auth header and return the bearer token.

        Args:
            req: The Request object.
            required: Flag for endpoints only accept authenticated requests.

        Raises:
            :class:`~gateway.dependencies.AAPIException`: if there is no token or it is not a Bearer token.

        Returns:
            The bearer token as string.
        """
        auth_header = super(TokenAuthenticator, self)._parse_auth_header(req, required)
        if auth_header is None:
            return None

        token_split = auth_header.split(" ")
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
            :class:`~gateway.dependencies.APIException`: If the token is not valid or the user does not have the
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
            user_entity = self.basic_token_handler.verify_token(token)
        elif method == "oidc":
            user_entity = self.oidc_token_handler.verify_token(token, **{"provider": provider})
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


class PasswordAuthenticator(BaseAuthenticator):
    """Authenticate a user by validating a password."""

    def validate(self, func: Callable, role: str, required: bool = False) -> Callable:
        """Decorator to authenticate a user by validating its password.

        Args:
            func: The wrapped function which the user wants to execute.
            role: The required role to execute the function (e.g.: user / admin).
            required: Flag for endpoints which only accept authenticated requests.

        Returns:
            The decorator function.
        """
        def password_decorator(*args: Any, **kwargs: Any) -> Union[Callable, Response]:
            """Validate a password and execute the provided function.

            The user object generated from the password is passed to the function as parameter 'user'.

            Returns:
                 The decorated function with the additional parameter user or a HTTP error
            """
            try:
                username_password = self._parse_auth_header(request, required=required)
                if not username_password:
                    raise APIException("A username and password need to be specified", 401, "gateway", internal=False)
                username, password = username_password.split(",")
                user_entity = self._rpc.users.get_user_entity_by_username(username=username)
                if not user_entity:
                    raise APIException(f"The user {username} does not exist in the database.", 401, "gateway",
                                       internal=False)
                if not self._verify_password(password, user_entity["password_hash"]):
                    raise APIException(f"Incorrect credentials for user {username}.", 401, "gateway", internal=False)
                return func(user=user_entity)
            except Exception as exc:
                return self._res.error(exc)
        return password_decorator

    def _parse_auth_header(self, req: Request, required: bool = False) -> Optional[str]:
        """Parse an auth header and return the username and password.

        Args:
            req: The Request object.
            required: Flag for endpoints only accept authenticated requests.

        Raises:
            :class:`~gateway.dependencies.APIException`: if there is no username / password or it is not Basic auth.

        Returns:
            The bearer token as string.
        """
        auth_header = super(PasswordAuthenticator, self)._parse_auth_header(req, required)
        if auth_header is None:
            return None

        token_split = auth_header.split(" ")
        if len(token_split) != 2 or token_split[0] != "Basic":
            raise APIException(
                msg="Invalid header for basic authentication.",
                code=401,
                service="gateway",
                internal=False)

        decoded = base64.b64decode(token_split[1]).decode('utf8')
        username, password = decoded.split(':')
        return ",".join([username, password])

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify the the password_hash matches the password."""
        return pwd_context.verify(password, password_hash)


class AuthenticationHandler:
    """Wrapper to add the appropriate authenticate decorator to a request depending on the requirements.

    This is the central entrypoint to add authentication to an API endpoint.
    """

    def __init__(self, rpc: FlaskPooledClusterRpcProxy, response_handler: ResponseParser, **kwargs: Any) -> None:
        """Initialize AuthenticationHandler."""
        self._token_auth = TokenAuthenticator(rpc, response_handler, **kwargs)
        self._password_auth = PasswordAuthenticator(rpc, response_handler, **kwargs)

    def authenticate(self, auth: AuthRequirement, func: Callable, role: str) -> Callable:
        """Decorate function with selected authentication."""
        if auth == AuthRequirement.token_required:
            return self._token_auth.validate(func, role, required=True)
        if auth == AuthRequirement.token_optional:
            return self._token_auth.validate(func, role, required=False)
        if auth == AuthRequirement.password_required:
            return self._password_auth.validate(func, role, required=True)
        else:  # AuthRequirement.password_optional
            return self._password_auth.validate(func, role, required=False)
