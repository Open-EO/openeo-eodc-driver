from uuid import uuid4

from marshmallow import Schema, fields, post_dump, post_load, pre_load

from gateway.users.models import Links, IdentityProviders


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
