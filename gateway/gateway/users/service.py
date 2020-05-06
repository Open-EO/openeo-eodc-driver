import os

from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

from passlib.apps import custom_app_context as pwd_context

import gateway.users.repository as rep
from gateway.dependencies.response import APIException
from .models import db, IdentityProviders, AuthType, Users, Profiles
from .schema import IdentityProviderSchema, UserSchema, ProfileSchema

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

    def get_user_info(self, user_id: str) -> dict:
        """Returns info about the (logged in) user.

        Returns:
            Dict -- 200 HTTP code
        """
        user = db.session.query(Users).filter_by(id=user_id).one()
        return {
            "status": "success",
            "code": 200,
            "data": UserSchema().dump(user),
        }

    def add_user(self, **user_args) -> dict:
        """
        Add Basic or OIDC user to database.

        Arguments:
            user_args {dict} -- The dictionary needed to add a user. Either [username, password, profile_name] > basic or
                [email, identity_provider, profile_name] > OIDC needs to be provided

        Returns:
            dict -- Describes success / failure of process
        """
        try:
            if 'email' in user_args and 'identity_provider' in user_args and 'profile' in user_args:
                out_user = user_args['email']
                user_args['auth_type'] = AuthType.oidc
                existing = rep.get_user_by_email(user_args['email'])

                user_args['identity_provider_id'] = rep.get_identity_provider_id(user_args.pop('identity_provider'))
                if not user_args['identity_provider_id']:
                    return ServiceException(400, 'None', 'The given identity provider is not supported').to_dict()

            elif 'username' in user_args and 'password' in user_args and 'profile' in user_args:
                out_user = user_args['username']
                user_args['auth_type'] = AuthType.basic
                existing = rep.get_user_by_username(user_args['username'])

            else:
                return ServiceException(400, 'None', 'User cannot be created! Please supply either username or email!').to_dict()
            if existing:
                return ServiceException(400, 'None', f"User {out_user} exists already in the database. Could not be"
                                                     f" added").to_dict()

            user_args['profile_id'] = rep.get_profile_id(user_args.pop('profile'))
            if not user_args['profile_id']:
                return ServiceException(400, 'None', 'The given profile is not supported').to_dict()

            user = UserSchema().load(user_args)
            db.session.add(user)
            db.session.commit()

            return {
                "status": "success",
                "code": 200,
                "data": {'message': f"User '{out_user}' successfully added to database."}
            }
        except Exception as exp:
            return ServiceException(500, 'None', str(exp)).to_dict()

    def delete_user(self, **user_args) -> dict:
        """
        Delete Basic or OIDC user from database.

        Arguments:
            user_args {dict} -- The dictionary needed to delete a user. Either [username] > basic or [email] > OIDC needs
                to be provided

        Returns:
            dict -- Describes success / failure of process
        """
        try:
            if 'username' in user_args:
                user = rep.get_user_by_username(user_args['username'])
                out_user = user_args['username']
            elif 'email' in user_args:
                user = rep.get_user_by_email(user_args['email'])
                out_user = user_args['email']
            else:
                return ServiceException(400, 'None', 'Either username or email needs to be provided!').to_dict()

            if user:
                db.session.delete(user)
                db.session.commit()

            return {
                "status": "success",
                "code": 200,
                "data": {'message': f"User '{out_user}' successfully delete from database."}
            }
        except Exception as exp:
            return ServiceException(500, 'None', str(exp)).to_dict()

    def add_user_profile(self, **profile_args) -> dict:
        """
        Add user profile to database.

        Arguments:
            profile_args {dict} -- Dictionary containing all required information to create a profile

        Returns:
            dict -- Describes success / failure of process
        """
        try:
            profile_name = profile_args['name']
            existing = db.session.query(Profiles).filter_by(name=profile_name).first()
            if existing:
                return ServiceException(400, 'None', f"Profile {profile_name} exists already "
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
            return ServiceException(500, 'None', str(exp)).to_dict()

    def delete_user_profile(self, **profile_args) -> dict:
        """
        Delete user profile from database.

        Arguments:
            profile_args {dict} -- Dictionary with key 'name' and value <profile-name>

        Returns:
            dict -- Describes success / failure of process
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
            return ServiceException(500, 'None', str(exp)).to_dict()

    def get_oidc_providers(self) -> dict:
        """Gets all available openID connect providers.

        Returns:
            Dict -- All available identity providers.
        """

        identity_providers = db.session.query(IdentityProviders).all()
        return {
            "status": "success",
            "code": 200,
            "data": IdentityProviderSchema(many=True).dump(identity_providers)
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
            return ServiceException(500, 'None', str(exp)).to_dict()


class BasicAuthService:

    service_name = 'gateway-auth'

    def get_basic_token(self, username: str, password: str) -> dict:
        """
        Generate token for basic user.

        Returns:
            Dict -- User_id with access token
        """
        if not username:
            raise APIException(f"A username needs to be specified", 401, "gateway", internal=False)
        user = db.session.query(Users).filter(Users.username == username).scalar()
        if not user:
            raise APIException(f"The user {username} does not exist in the database.", 401, "gateway", internal=False)
        if not self.verify_password(user, password):
            raise APIException(f"Incorrect credentials for user {username}.", 401, "gateway", internal=False)
        return {
            "status": "success",
            "code": 200,
            "data":  {"access_token": self.generate_auth_token(user)},
        }

    def verify_password(self, user: Users, password: str):
        return pwd_context.verify(password, user.password_hash)

    def generate_auth_token(self, user: Users, expiration: int = 600):
        serialized = Serializer(os.environ.get('SECRET_KEY'), expires_in=expiration)
        return serialized.dumps({'id': user.id}).decode('utf-8')

    def verify_auth_token(self, token):
        # Verify token
        s = Serializer(os.environ.get('SECRET_KEY'))
        try:
            data = s.loads(token)
        except SignatureExpired:
            return  # valid token, but expired
        except BadSignature:
            return  # invalid token

        # Verify user exists
        user = db.session.query(Users).filter(Users.id == data['id']).scalar()
        return user.id if user else None
