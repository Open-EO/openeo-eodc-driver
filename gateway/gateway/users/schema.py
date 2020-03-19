from uuid import uuid4

from marshmallow import Schema, fields, post_dump, post_load, pre_load
from passlib.apps import custom_app_context as pwd_context

from gateway.users.models import Links, IdentityProviders, Users, db, Profiles, Storage


class BaseSchema(Schema):
    __skip_values__ = [None, []]
    __model__ = None

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value not in self.__skip_values__
        }

    @post_load
    def make_object(self, data, **kwargs):
        if self.__model__:
            return self.__model__(**data)


class LinkSchema(BaseSchema):
    __model__ = Links

    rel = fields.String(required=True)
    href = fields.Url(required=True)
    type = fields.String()
    title = fields.String()


class IdentityProviderSchema(BaseSchema):
    __model__ = IdentityProviders

    id_internal = fields.String(attribute='id', required=True)
    id = fields.String(attribute='id_openeo', required=True)
    issuer = fields.String(attribute='issuer_url', required=True)
    scopes = fields.String(required=True)
    title = fields.String(required=True)
    description = fields.String()
    links = fields.List(fields.Nested(LinkSchema))

    @pre_load
    def preload(self, in_data, **kwargs):
        in_data['id_internal'] = 'ip-' + str(uuid4())
        in_data['scopes'] = ','.join(in_data['scopes'])
        return in_data


class StorageSchema(BaseSchema):
    __model__ = Storage

    free = fields.Integer(required=True)
    quota = fields.Integer(required=True)


class UserSchema(BaseSchema):
    __model__ = Users

    user_id = fields.String(attribute='id', required=True)
    budget = fields.Method('to_euro', deserialize='to_cent')
    links = fields.List(fields.Nested(LinkSchema))
    storage = fields.Nested(StorageSchema)

    auth_type = fields.Field(load_only=True)
    role = fields.String(load_only=True, default="user")
    username = fields.String(load_only=True)
    password_hash = fields.Method(deserialize='get_password_hash', load_only=True, data_key='password')
    email = fields.String(load_only=True)
    identity_provider_id = fields.String(load_only=True)
    profile_id = fields.String(load_only=True)

    @pre_load
    def get_id(self, in_data, **kwargs):
        if 'user_id' not in in_data:
            in_data['user_id'] = 'us-' + str(uuid4())
        return in_data

    def get_password_hash(self, obj):
        if obj:
            return pwd_context.encrypt(obj)

    def to_cent(self, obj):
        if obj:
            return int(obj * 100)

    def to_euro(self, obj):
        if obj:
            return obj.budget / 100.0


class ProfileSchema(BaseSchema):
    __model__ = Profiles

    id = fields.String(required=True)
    name = fields.String(required=True)
    data_access = fields.String(required=True)

    @pre_load
    def add_id(self, in_data, **kwargs):
        if 'id' not in in_data:
            in_data['id'] = 'pr-' + str(uuid4())
        return in_data
