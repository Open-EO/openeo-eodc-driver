"""Provides the implementation of the user management service and service exception."""
import logging
from typing import Any, Dict, Optional, Tuple

from nameko.rpc import rpc
from nameko_sqlalchemy import DatabaseSession

import users.dependencies.repository as rep
from users.dependencies.settings import initialise_settings
from users.models import AuthType, Base, IdentityProviders, Profiles, Users
from users.schema import IdentityProviderSchema, ProfileSchema, UserSchema

service_name = "users"
LOGGER = logging.getLogger("standardlog")
initialise_settings()


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
        LOGGER.exception(msg, exc_info=True)

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

    name = service_name
    db = DatabaseSession(Base)
    """Database connection to user database."""

    @rpc
    def get_user_info(self, user: Dict[str, Any]) -> dict:
        """Return info about the (logged in) user.

        Returns:
            200 HTTP code and details about the user.
        """
        try:
            user_obj = self.db.query(Users).filter_by(id=user["id"]).one()
            LOGGER.info(f"Return user info about {user_obj.id}")
            return {
                "status": "success",
                "code": 200,
                "data": UserSchema().dump(user_obj),
            }
        except Exception as exp:
            return ServiceException(service_name, 500, str(exp), self._get_user_id(user)).to_dict()

    @rpc
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
                existing = rep.get_user_by_email(self.db, user_args['email'])

                user_args['identity_provider_id'] =\
                    rep.get_identity_provider_id(self.db, user_args.pop('identity_provider'))
                if not user_args['identity_provider_id']:
                    return ServiceException(service_name, 400, 'The given identity provider is not supported') \
                        .to_dict()

            elif 'username' in user_args and 'password' in user_args and 'profile' in user_args:
                out_user = user_args['username']
                user_args['auth_type'] = AuthType.basic
                existing = rep.get_user_by_username(self.db, user_args['username'])

            else:
                return ServiceException(service_name, 400, 'User cannot be created! Please supply ensure you'
                                                           ' supplied all  required information! (email -'
                                                           ' identity_provider - profile or username - password'
                                                           ' - profile)').to_dict()
            if existing:
                return ServiceException(service_name, 400, f"User {out_user} exists already in the database."
                                                           f" Could not be added").to_dict()

            user_args['profile_id'] = rep.get_profile_id(self.db, user_args.pop('profile'))
            if not user_args['profile_id']:
                return ServiceException(service_name, 400, 'The given profile is not supported').to_dict()

            user = UserSchema().load(user_args)
            self.db.add(user)
            self.db.commit()

            LOGGER.info(f"User '{out_user}' successfully added to database")
            return {
                "status": "success",
                "code": 200,
                "data": {"message": f"User '{out_user}' successfully added to database."}
            }
        except Exception as exp:
            return ServiceException(service_name, 500, str(exp)).to_dict()

    @rpc
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
                out_user = user_args['username']
                user = rep.get_user_by_username(self.db, user_args['username'])
            elif 'email' in user_args:
                out_user = user_args['email']
                user = rep.get_user_by_email(self.db, user_args['email'])
            else:
                return ServiceException(service_name, 400, 'Either username or email needs to be provided!').to_dict()

            if user:
                self.db.delete(user)
                self.db.commit()

            LOGGER.info(f"User '{out_user}' successfully removed from database.")
            return {
                "status": "success",
                "code": 200,
                "data": {'message': f"User '{out_user}' successfully removed from database."}
            }
        except Exception as exp:
            return ServiceException(service_name, 500, str(exp), self._get_user_id(user)).to_dict()

    @rpc
    def add_user_profile(self, **profile_args: Any) -> dict:
        """Add user profile to database.

        Args:
            profile_args: Dictionary containing all required information to create a profile.

        Returns:
            Describes success / failure of process
        """
        try:
            profile_name = profile_args['name']
            existing = self.db.query(Profiles).filter_by(name=profile_name).first()
            if existing:
                return ServiceException(service_name, 400, f"Profile {profile_name} exists already "
                                                           f"in the database. Could not be added").to_dict()
            profile = ProfileSchema().load(profile_args)
            self.db.add(profile)
            self.db.commit()

            LOGGER.info(f"Profile '{profile_name}' added to database.")
            return {
                "status": "success",
                "code": 200,
                "data": {'message': f"Profile '{profile_name}' added to database."}
            }
        except Exception as exp:
            return ServiceException(service_name, 500, str(exp)).to_dict()

    @rpc
    def delete_user_profile(self, **profile_args: Any) -> dict:
        """Delete user profile from database.

        Args:
            profile_args: Dictionary with key 'name' and value <profile-name>.

        Returns:
            Describes success / failure of process.
        """
        try:
            profile_name = profile_args['name']
            profile = self.db.query(Profiles).filter_by(name=profile_name).first()
            if profile:
                self.db.delete(profile)
                self.db.commit()
            LOGGER.info(f"Profile '{profile_name}' removed from database.")
            return {
                "status": "success",
                "code": 200,
                "data": {'message': f"Profile '{profile_name}' removed from database."}
            }
        except Exception as exp:
            return ServiceException(service_name, 500, str(exp)).to_dict()

    @rpc
    def get_oidc_providers(self, user: Dict[str, Any] = None) -> dict:
        """Return all available openID connect providers as dictionary."""
        try:
            identity_providers = self.db.query(IdentityProviders).all()
            id_providers = {'providers': IdentityProviderSchema(many=True).dump(identity_providers)}
            # update scopes from string to list
            for item in id_providers['providers']:
                item['scopes'] = item['scopes'].split(",")
            LOGGER.info("Return available identity providers.")
            return {
                "status": "success",
                "code": 200,
                "data": id_providers
            }
        except Exception as exp:
            return ServiceException(service_name, 500, str(exp)).to_dict()

    @rpc
    def add_identity_provider(self, **identity_provider_args: Any) -> dict:
        """Add Identity provider to database for OIDC authentication.

        Args:
            identity_provider_args: Dictionary providing all required information of a identity provider.

        Returns:
            Describes success / failure of process.
        """
        try:
            existing = self.db.query(IdentityProviders).filter_by(id_openeo=identity_provider_args['id']).first()
            if existing:
                return ServiceException(service_name, 400, f"Identity Provider {identity_provider_args['id']}"
                                                           f" exists already in the database. Could not be"
                                                           f" added").to_dict()

            identity_provider = IdentityProviderSchema().load(identity_provider_args)
            self.db.add(identity_provider)
            self.db.commit()

            LOGGER.info(f"Identity provider '{identity_provider.id_openeo}' added to database.")
            return {
                "status": "success",
                "code": 200,
                "data": {'message': f"Identity provider '{identity_provider.id_openeo}' added to database."}
            }
        except Exception as exp:
            return ServiceException(service_name, 500, str(exp)).to_dict()

    @rpc
    def delete_identity_provider(self, **identity_provider_args: Any) -> dict:
        """Delete Identity provider from database.

        Args:
            identity_provider_args: A dictionary containing the id of the identity provider to be removed.

        Returns:
            Describes success / failure of process.
        """
        try:
            id_openeo = identity_provider_args['id']
            identity_provider = self.db.query(IdentityProviders).filter_by(id_openeo=id_openeo).first()
            if identity_provider:
                self.db.delete(identity_provider)
                self.db.commit()
            LOGGER.info(f"Identity provider {id_openeo} successfully deleted.")
            return {
                "status": "success",
                "code": 200,
                "data": {"message": f"Identity provider {id_openeo} successfully deleted."}
            }
        except Exception as exp:
            return ServiceException(service_name, 500, str(exp)).to_dict()

    def _get_user_id(self, user: Optional[Dict[str, Any]]) -> Optional[str]:
        """Return the user_id if a user object is given."""
        if user and "id" in user:
            return user["id"]
        return None

    @rpc
    def get_user_entity_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Return the user dict from user_id."""
        return rep.get_user_entity(self.db, rep.get_user_by_id, **{"user_id": user_id})

    @rpc
    def get_user_entity_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Return the user dict from its email."""
        return rep.get_user_entity(self.db, rep.get_user_by_email, **{"email": email})

    @rpc
    def get_user_entity_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Return the user dict from its username."""
        return rep.get_user_entity(self.db, rep.get_user_by_username, **{"username": username})

    @rpc
    def check_oidc_issuer_exists(self, identity_provider_id_openo: str) -> Tuple[bool, Optional[str]]:
        """Check the given identity provider exists in the database."""
        identity_provider = self.db.query(IdentityProviders).filter_by(id_openeo=identity_provider_id_openo).first()
        if identity_provider:
            return True, identity_provider.issuer_url
        return False, None
