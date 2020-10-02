"""Provides the implementation of the user management service and service exception."""
from typing import Any, Dict, Optional

from itsdangerous import (BadSignature, SignatureExpired, TimedJSONWebSignatureSerializer as Serializer)
from passlib.apps import custom_app_context as pwd_context

import gateway.users.repository as rep
from gateway.dependencies.response import APIException
from .models import AuthType, IdentityProviders, Profiles, Users, db
from .repository import get_user_entity_from_id
from .schema import IdentityProviderSchema, ProfileSchema, UserSchema

service_name = "gateway-users"


class ServiceException(Exception):
    """ServiceException is raised if an exception occurred while processing the request.

    The ServiceException is mapping any exception to a serializable format for the API gateway.

    Attributes:
        service: The name of the service as string.
        code: An integer holding the error code.
        user_id: The id of the user as string. (default: None)
        msg: A string with the error message.
        internal: A boolean indicating if this is an internal error. (default: True)
        links: A list of links which can be useful when getting this error. (default: None)
    """

    def __init__(self, service: str, code: int, msg: str, user_id: str = None, internal: bool = True,
                 links: list = None) -> None:
        """Initialize service exception."""
        if not links:
            links = ['/users_mng/users', '/users_mng/user_profiles', '/users_mng/oidc_providers']

        self._service = service
        self._code = code
        self._user_id = user_id
        self._msg = msg
        self._internal = internal
        self._links = links

    def to_dict(self) -> dict:
        """Serialize the object to a dict.

        Returns:
            dict -- The serialized exception
        """
        return {
            "status": "error",
            "service": self._service,
            "code": self._code,
            "user_id": self._user_id,
            "msg": self._msg,
            "internal": self._internal,
            "links": self._links,
        }


class UsersService:
    """Management of user and connected components.

    This includes adding / removing users, profiles, identity_providers and providing detailed information about a user
    or identity_provider.
    """

    def get_user_info(self, user: Dict[str, Any]) -> dict:
        """Returns info about the (logged in) user.

        Returns:
            200 HTTP code and details about the user.
        """
        try:
            user = db.session.query(Users).filter_by(id=user["id"]).one()
            return {
                "status": "success",
                "code": 200,
                "data": UserSchema().dump(user),
            }
        except Exception as exp:
            return ServiceException(service_name, 500, str(exp), self._get_user_id(user)).to_dict()

    def add_user(self, **user_args: Any) -> dict:
        """Add Basic or OIDC user to database.

        Args:
            user_args: The dictionary needed to add a user. Either [username, password, profile_name] > basic or
                [email, identity_provider, profile_name] > OIDC needs to be provided.

        Returns:
            Describes success / failure of process.
        """
        try:
            if 'email' in user_args and 'identity_provider' in user_args and 'profile' in user_args:
                out_user = user_args['email']
                user_args['auth_type'] = AuthType.oidc
                existing = rep.get_user_by_email(user_args['email'])

                user_args['identity_provider_id'] = rep.get_identity_provider_id(user_args.pop('identity_provider'))
                if not user_args['identity_provider_id']:
                    return ServiceException(service_name, 400, 'The given identity provider is not supported') \
                        .to_dict()

            elif 'username' in user_args and 'password' in user_args and 'profile' in user_args:
                out_user = user_args['username']
                user_args['auth_type'] = AuthType.basic
                existing = rep.get_user_by_username(user_args['username'])

            else:
                return ServiceException(service_name, 400, 'User cannot be created! Please supply ensure you'
                                                           ' supplied all  required information! (email -'
                                                           ' identity_provider - profile or username - password'
                                                           ' - profile)').to_dict()
            if existing:
                return ServiceException(service_name, 400, f"User {out_user} exists already in the database."
                                                           f" Could not be added").to_dict()

            user_args['profile_id'] = rep.get_profile_id(user_args.pop('profile'))
            if not user_args['profile_id']:
                return ServiceException(service_name, 400, 'The given profile is not supported').to_dict()

            user = UserSchema().load(user_args)
            db.session.add(user)
            db.session.commit()

            return {
                "status": "success",
                "code": 200,
                "data": {'message': f"User '{out_user}' successfully added to database."}
            }
        except Exception as exp:
            return ServiceException(service_name, 500, str(exp)).to_dict()

    def delete_user(self, **user_args: Any) -> dict:
        """Delete Basic or OIDC user from database.

        Args:
            user_args: The dictionary needed to delete a user. Either [username] > basic or [email] > OIDC needs
                to be provided.

        Returns:
            Describes success / failure of process.
        """
        user = None
        try:
            if 'username' in user_args:
                user = rep.get_user_by_username(user_args['username'])
                out_user = user_args['username']
            elif 'email' in user_args:
                user = rep.get_user_by_email(user_args['email'])
                out_user = user_args['email']
            else:
                return ServiceException(service_name, 400, 'Either username or email needs to be provided!').to_dict()

            if user:
                db.session.delete(user)
                db.session.commit()

            return {
                "status": "success",
                "code": 200,
                "data": {'message': f"User '{out_user}' successfully delete from database."}
            }
        except Exception as exp:
            return ServiceException(service_name, 500, str(exp), self._get_user_id(user)).to_dict()

    def add_user_profile(self, **profile_args: Any) -> dict:
        """Add user profile to database.

        Args:
            profile_args: Dictionary containing all required information to create a profile.

        Returns:
            dict -- Describes success / failure of process
        """
        try:
            profile_name = profile_args['name']
            existing = db.session.query(Profiles).filter_by(name=profile_name).first()
            if existing:
                return ServiceException(service_name, 400, f"Profile {profile_name} exists already "
                                                           f"in the database. Could not be added").to_dict()
            profile = ProfileSchema().load(profile_args)
            db.session.add(profile)
            db.session.commit()

            return {
                "status": "success",
                "code": 200,
                "data": {'message': f"Profile '{profile_name}' added to database."}
            }
        except Exception as exp:
            return ServiceException(service_name, 500, str(exp)).to_dict()

    def delete_user_profile(self, **profile_args: Any) -> dict:
        """Delete user profile from database.

        Args:
            profile_args: Dictionary with key 'name' and value <profile-name>.

        Returns:
            Describes success / failure of process.
        """
        try:
            profile_name = profile_args['name']
            profile = db.session.query(Profiles).filter_by(name=profile_name).first()
            if profile:
                db.session.delete(profile)
                db.session.commit()
            return {
                "status": "success",
                "code": 200,
                "data": {'message': f"Profile '{profile_name}' delete from database."}
            }
        except Exception as exp:
            return ServiceException(service_name, 500, str(exp)).to_dict()

    def get_oidc_providers(self) -> dict:
        """Return all available openID connect providers as dictionary."""
        try:
            identity_providers = db.session.query(IdentityProviders).all()
            id_providers = {'providers': IdentityProviderSchema(many=True).dump(identity_providers)}
            # update scopes from string to list
            for item in id_providers['providers']:
                item['scopes'] = item['scopes'].split(",")

            return {
                "status": "success",
                "code": 200,
                "data": id_providers
            }
        except Exception as exp:
            return ServiceException(service_name, 500, str(exp)).to_dict()

    def add_identity_provider(self, **identity_provider_args: Any) -> dict:
        """Add Identity provider to database for OIDC authentication.

        Args:
            identity_provider_args: Dictionary providing all required information of a identity provider.

        Returns:
            Describes success / failure of process.
        """
        try:
            existing = db.session.query(IdentityProviders).filter_by(id_openeo=identity_provider_args['id']).first()
            if existing:
                return ServiceException(service_name, 400, f"Identity Provider {identity_provider_args['id']}"
                                                           f" exists already in the database. Could not be"
                                                           f" added").to_dict()

            identity_provider = IdentityProviderSchema().load(identity_provider_args)
            db.session.add(identity_provider)
            db.session.commit()

            return {
                "status": "success",
                "code": 200,
                "data": {'message': f"Identity provider '{identity_provider.id_openeo}' added to database."}
            }
        except Exception as exp:
            return ServiceException(service_name, 500, str(exp)).to_dict()

    def delete_identity_provider(self, **identity_provider_args: Any) -> dict:
        """Delete Identity provider from database.

        Args:
            identity_provider_args: A dictionary containing the id of the identity provider to be removed.

        Returns:
            Describes success / failure of process.
        """
        try:
            id_openeo = identity_provider_args['id']
            identity_provider = IdentityProviders.query.filter_by(id_openeo=id_openeo).first()
            if identity_provider:
                db.session.delete(identity_provider)
                db.session.commit()
            return {
                "status": "success",
                "code": 200,
                "data": {"message": f"Identity provider {id_openeo} successfully deleted."}
            }
        except Exception as exp:
            return ServiceException(service_name, 500, str(exp)).to_dict()

    def _get_user_id(self, user: Optional[Dict[str, Any]]) -> Optional[str]:
        if user and "id" in user:
            return user["id"]
        return None


class BasicAuthService:
    """Handler basic authentication."""

    service_name = 'gateway-auth'

    def __init__(self, secret_key: str) -> None:
        """Initialize BasicAuthService."""
        self.secret_key = secret_key

    def get_basic_token(self, username: str, password: str) -> dict:
        """Generate and return access token for basic user."""
        if not username:
            raise APIException("A username needs to be specified", 401, "gateway", internal=False)
        user = db.session.query(Users).filter(Users.username == username).scalar()
        if not user:
            raise APIException(f"The user {username} does not exist in the database.", 401, "gateway", internal=False)
        if not self.verify_password(user, password):
            raise APIException(f"Incorrect credentials for user {username}.", 401, "gateway", internal=False)
        return {
            "status": "success",
            "code": 200,
            "data": {"access_token": self.generate_auth_token(user)},
        }

    def verify_password(self, user: Users, password: str) -> bool:
        """Verify the the password matches the user."""
        return pwd_context.verify(password, user.password_hash)

    def generate_auth_token(self, user: Users, expiration: int = 600) -> str:
        """Generate and return access token for user."""
        serialized = Serializer(self.secret_key, expires_in=expiration)
        return serialized.dumps({'id': user.id}).decode('utf-8')

    def verify_auth_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify access token is valid.

        Returns:
            If token is valid the corresponding user object otherwise None.
        """
        # Verify token
        s = Serializer(self.secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token

        # Verify user exists
        return get_user_entity_from_id(data["id"])
