""" AuthenticationHandler """

from typing import Union, Optional

import jwt
import requests
from flask import request
from flask.wrappers import Request

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

        # TODO from version > 0.4.2 the token will contain basic or oidc and no "brute force" approach will be needed
        user_id = self._verify_basic_token(token)
        if not user_id:
            user_id = self._verify_oidc_token(token)

        if not role == 'user':
            if not self._check_user_role(user_id, role=role):
                user_id = None  # User does not have 'admin' role and is therefore not allowed to access the endpoint

        if not user_id:
            raise APIException(
                msg='Invalid token. User could not be authenticated.',
                code=401,
                service="gateway",
                internal=False)
        return user_id

    def _verify_basic_token(self, token) -> Optional[str]:
        """
        Verifies a basic token.
        """
        from gateway.users.repository import verify_auth_token
        return verify_auth_token(token)[0]

    def _verify_oidc_token(self, token) -> Optional[str]:
        """
        Verifies OIDC token.
        """

        token_header = jwt.get_unverified_header(token)
        token_unverified = jwt.decode(token, verify=False)

        # Currently an invalid basic token is also tried as OIDC token, which creates not meaningful errors
        if 'email' not in token_unverified or 'iss' not in token_unverified:
            return None
        user_id = self._get_user_id_from_email(token_unverified['email'])
        _ = self._check_oidc_issuer_exists(token_unverified['iss'])

        jwks = self._get_auth_jwks(token_unverified['iss'] + "/.well-known/openid-configuration")
        if jwks:
            public_key = None
            for key in jwks['keys']:
                if key['kid'] == token_header['kid']:
                    public_key = rsa_pem_from_jwk(key)

            if not jwt.decode(token,
                              public_key,
                              verify=True,
                              algorithms=token_header['alg'],
                              audience=token_unverified['azp'],
                              issuer=token_unverified['iss']):
                raise APIException(
                    msg="Invalid OIDC token (cannot be decoded). User cannot be authenticated."
                )
            return user_id

    def _get_user_id_from_email(self, user_email: str) -> str:
        """
        Checks the email exists in the database and gets the corresponding user_id.
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
        """

        from gateway.users.models import db, Users

        if not role == db.session.query(Users.role).filter(Users.id == user_id).scalar():
            raise APIException(
                msg=f"The user {user_id} is not authorized to perform this operation.",
                code=403,
                service="gateway",
                internal=False)
        return True

    def _check_oidc_issuer_exists(self, issuer: str) -> bool:
        """
        Checks the given issuer_url exists in the database.
        """
        from gateway.users.models import db, IdentityProviders
        identity_provider = db.session.query(IdentityProviders).filter(IdentityProviders.issuer_url == issuer).first()
        if not identity_provider:
            raise APIException(
                msg="The given issuer url is not supported.",
                code=401,
                service="gateway",
                internal=False)
        return True

    def _get_auth_jwks(self, oidc_well_known_url: str) -> dict:

        jwks = None
        response = requests.get(oidc_well_known_url)
        if response.status_code == 200:
            jwks_uri = response.json()['jwks_uri']
            response = requests.get(jwks_uri)
            if response.status_code == 200:
                jwks = response.json()

        return jwks
