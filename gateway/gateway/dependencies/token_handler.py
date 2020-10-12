"""Classes to handler different types of token authentication and generation of tokens."""
from abc import ABC, abstractmethod
from typing import Any, Dict

import requests
from dynaconf import settings
from flask_nameko import FlaskPooledClusterRpcProxy
from itsdangerous import (BadSignature, SignatureExpired, TimedJSONWebSignatureSerializer as Serializer)

from .response import APIException


class BaseTokenHandler(ABC):
    """Base class to handler tokens."""

    def __init__(self, rpc: FlaskPooledClusterRpcProxy) -> None:
        """Initialize base token handler class."""
        self._rpc = rpc

    @abstractmethod
    def verify_token(self, token: str, **kwargs: Any) -> Dict[str, Any]:
        """Verify a token and return corresponding user dict for valid tokens."""
        pass


class BasicTokenHandler(BaseTokenHandler):
    """Token handler working on tokens from basic auth."""

    def __init__(self, rpc: FlaskPooledClusterRpcProxy) -> None:
        """Initialize BasicTokenHandler."""
        super(BasicTokenHandler, self).__init__(rpc)
        self.secret_key = settings.SECRET_KEY

    def get_token(self, user: Dict[str, Any]) -> dict:
        """Generate and return access token for basic user.

        This function should be thought of API function assuming prior basic (password) authentication.
        And the result will passed to the :class:`~gateway.dependencies.response.ResponseParser`.
        """
        return {
            "status": "success",
            "code": 200,
            "data": {"access_token": self._generate_basic_auth_token(user["id"])},
        }

    def _generate_basic_auth_token(self, user_id: str, expiration: int = 600) -> str:
        """Generate and return access token for basic user."""
        serialized = Serializer(self.secret_key, expires_in=expiration)
        return serialized.dumps({'id': user_id}).decode('utf-8')

    def verify_token(self, token: str, **kwargs: Any) -> Dict[str, Any]:
        """Verify a basic token.

        Args:
            token: The basic authentication token.
            **kwargs: Auxiliary arguments - not used here.

        Raises:
            :class:`~gateway.dependencies.APIException`: If the token is not valid or expired.

        Returns:
            The user object corresponding to the token or None if the token is invalid.
        """
        s = Serializer(self.secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            raise APIException(
                msg="Basic auth token is expired.",
                code=401,
                service="gateway",
                internal=False,
            )
        except BadSignature:
            raise APIException(
                msg="Invalid basic auth token.",
                code=401,
                service="gateway",
                internal=False,
            )
        return self._rpc.users.get_user_entity_by_id(user_id=data["id"])


class OidcTokenHandler(BaseTokenHandler):
    """Token handler working on tokens from OIDC providers."""

    def verify_token(self, token: str, **kwargs: Any) -> Dict[str, Any]:
        """Verify OIDC token.

        Args:
            token: The OIDC authentication token (of type access-token)
            **kwargs: Auxiliary arguments
                key 'provider' needs to be set: The used OIDC provider ID (must be supported by backend)

        Raises:
            :class:`~gateway.dependencies.APIException`: If the token is not valid.

        Returns:
            The user object corresponding to the token
        """
        # Get user from OIDC /userinfo endpoint
        provider_wellknown = self._check_oidc_issuer_exists(kwargs["provider"])
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
        return self._rpc.users.get_user_entity_by_email(email=userinfo.json()["email"])

    def _check_oidc_issuer_exists(self, id_openeo: str) -> str:
        """Check the given identity provider exists in the database.

        Args:
            id_openeo: The id to check.

        Raises:
            :class:`~gateway.dependencies.APIException`: If the issuer_url is not supported.

        Returns:
            True and the issuer's well-known url if the identity provider exists.
        """
        exists, issuer_url = self._rpc.users.check_oidc_issuer_exists(id_openeo)
        if not exists:
            raise APIException(
                msg=f"The given Identity Provider '{id_openeo}' is not supported.",
                code=401,
                service="gateway",
                internal=False)
        return issuer_url + "/.well-known/openid-configuration"
