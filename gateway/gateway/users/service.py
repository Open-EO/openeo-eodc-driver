import gateway.users.repository as rep
from .models import db, IdentityProviders, AuthType, Users
from .schema import IdentityProviderSchema, UserSchema

service_name = "gateway-users"


class ServiceException(Exception):
    """ServiceException raises if an exception occurs while processing the
    request. The ServiceException is mapping any exception to a serializable
    format for the API gateway.
    """

    def __init__(self, code: int, user_id: str, msg: str, internal: bool = True, links: list = None):
        if not links:
            links = ['/users_mng/users', '/users_mng/user_profiles', '/users_mng/oidc_providers']

        self._service = service_name
        self._code = code
        self._user_id = user_id
        self._msg = msg
        self._internal = internal
        self._links = links
        # LOGGER.exception(msg, exc_info=True)

    def to_dict(self) -> dict:
        """Serializes the object to a dict.

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
    """
    User Management.
    """

    def add_user(self, **kwargs) -> dict:
        """
        Add Basic or OIDC user to database.

        Arguments:
            kwargs {dict} -- The dictionary needed to add a user. Either [username, password, profile_name] > basic or
                [email, identity_provider, profile_name] > OIDC needs to be provided

        Returns:
            dict -- Describes success / failure of process
        """

        if 'username' in kwargs and 'password' in kwargs and 'profile_name' in kwargs:
            worked, exc = rep.insert_users(auth_type='basic', **kwargs)
            out_user = kwargs['username']
        elif 'email' in kwargs and 'identity_provider' in kwargs and 'profile_name' in kwargs:
            worked, exc = rep.insert_users(auth_type='oidc', **kwargs)
            out_user = kwargs['email']
        else:
            return ServiceException(400, 'None', 'User cannot be created! Please supply either username or email!').to_dict()

        if not worked:
            # TODO currently complete stack trace is returned (good for debugging!), could be maybe put into log?
            return ServiceException(500, out_user, f"Failed to create user '{out_user}'.\n{exc}").to_dict()
        return {
            "status": "success",
            "code": 200,
            "data": {'message': f"User '{out_user}' successfully added to database."}
        }

    def delete_user(self, **kwargs) -> dict:
        """
        Delete Basic or OIDC user from database.

        Arguments:
            kwargs {dict} -- The dictionary needed to delete a user. Either [username] > basic or [email] > OIDC needs
                to be provided

        Returns:
            dict -- Describes success / failure of process
        """
        if 'username' in kwargs:
            worked, exc = rep.delete_user_username(kwargs['username'])
            out_user = kwargs['username']
        elif 'email' in kwargs:
            worked, exc = rep.delete_user_email(kwargs['email'])
            out_user = kwargs['email']
        else:
            return ServiceException(500, 'None', 'Either username or email needs to be provided!').to_dict()

        if not worked:
            return ServiceException(500, out_user, f"Failed to create user '{out_user}'.\n{exc}").to_dict()
        return {
            "status": "success",
            "code": 200,
            "data": {'message': f"User '{out_user}' successfully delete from database."}
        }

    def add_user_profile(self, name: str, data_access: str) -> dict:
        """
        Add user profile to database.

        Arguments:
            name {str} -- The name of the profile to add
            data_access {str} -- The string describing the single data access levels separated by comma
                (e.g. basic,projectA)

        Returns:
            dict -- Describes success / failure of process
        """
        worked, exc = rep.insert_profile(name, data_access)
        if not worked:
            return ServiceException(500, 'None', f"Profile '{name}' could not be added to the database.\n{exc}").to_dict()
        return {
            "status": "success",
            "code": 200,
            "data": {'message': f"Profile '{name}' added to database."}
        }

    def delete_user_profile(self, name: str) -> dict:
        """
        Delete user profile from database.

        Arguments:
            name {str} -- The name of the profile to delete

        Returns:
            dict -- Describes success / failure of process
        """
        worked, exc = rep.delete_profile(name)
        if not worked:
            return ServiceException(500, 'None', f"Profile '{name}' could not be delete from database.\n{exc}").to_dict()
        return {
            "status": "success",
            "code": 200,
            "data": {'message': f"Profile '{name}' delete from database."}
        }

    def add_identity_provider(self, **identity_provider_args) -> dict:
        """
        Add Identity provider to database for OIDC authentication.

        Arguments:
            **identity_provider_args {dict} -- Dictionary providing all required information of a identity provider

        Returns:
            dict -- Describes success / failure of process
        """
        try:
            existing = db.session.query(IdentityProviders).filter_by(id_openeo=identity_provider_args['id']).first()
            if existing:
                return ServiceException(400, 'None', f"Identity Provider {identity_provider_args['id']} exists already "
                                                     f"in the database. Could not be added").to_dict()

            identity_provider = IdentityProviderSchema().load(identity_provider_args)
            db.session.add(identity_provider)
            db.session.commit()

            return {
                "status": "success",
                "code": 200,
                "data": {'message': f"Identity provider '{identity_provider.id_openeo}' added to database."}
            }
        except Exception as exp:
            return ServiceException(500, 'None', str(exp)).to_dict()

    def delete_identity_provider(self, **identity_provider_args) -> dict:
        """
        Delete Identity provider from database.

        Arguments:
            id_openeo {str} -- The OpenEO ID of the identity provider to delete

        Returns:
            dict -- Describes success / failure of process
        """
        try:
            id_openeo = identity_provider_args['id']
            identity_provider = IdentityProviders.query.filter(IdentityProviders.id_openeo == id_openeo).first()
            if identity_provider:
                db.session.delete(identity_provider)
                db.session.commit()
            return {
                "status": "success",
                "code": 200,
                "data": {"message": f"Identity provider {id_openeo} successfully deleted."}
            }
        except Exception as exp:
            return ServiceException(500, 'None', str(exp)).to_dict()
