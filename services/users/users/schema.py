"""Provides all schemas definitions used in the main service to serialize and deserialize data."""
from typing import Any, List, Optional
from uuid import uuid4

from marshmallow import Schema, fields, post_dump, post_load, pre_load
from passlib.apps import custom_app_context as pwd_context

from users.models import Base, IdentityProviders, Links, Profiles, Storage, Users


class BaseSchema(Schema):
    """Base Schema including functionality useful in all other schemas."""

    __skip_values__: List[Any] = [None, []]
    """Key value pairs where the value is one of these will not be dumped.

    There is no need to return unset keys and overload returned dictionaries with 'meaningless' key value pairs.
    """
    __model__: Base = None
    """Database model table class."""

    @post_dump
    def remove_skip_values(self, data: dict, **kwargs: Any) -> dict:
        """Remove keys where value is in __skip_values__."""
        return {
            key: value for key, value in data.items()
            if value not in self.__skip_values__
        }

    @post_load
    def make_object(self, data: dict, **kwargs: Any) -> Base:
        """Create a database object from a deserialized object."""
        if self.__model__:
            return self.__model__(**data)


class LinkSchema(BaseSchema):
    """Schema to store details about a link."""

    __model__ = Links

    rel = fields.String(required=True)
    href = fields.Url(required=True)
    type_ = fields.String(data_key="type", attribute="type")
    title = fields.String()


class IdentityProviderSchema(BaseSchema):
    """Schema to store details about an identity provider."""

    __model__ = IdentityProviders

    id_internal = fields.String(attribute="id", load_only=True)
    id_ = fields.String(data_key="id", attribute="id_openeo", required=True)
    issuer = fields.String(attribute="issuer_url", required=True)
    scopes = fields.String(required=True)
    title = fields.String(required=True)
    description = fields.String()
    links = fields.List(fields.Nested(LinkSchema))

    @pre_load
    def preload(self, in_data: dict, **kwargs: Any) -> dict:
        """Create an internal id and reformat scopes to insert them into the database."""
        in_data["id_internal"] = "ip-" + str(uuid4())
        in_data["scopes"] = ",".join(in_data["scopes"])
        return in_data


class StorageSchema(BaseSchema):
    """Schema to store details about storage."""

    __model__ = Storage

    free = fields.Integer(required=True)
    quota = fields.Integer(required=True)


class UserSchema(BaseSchema):
    """Schema to store details about a user."""

    __model__ = Users

    user_id = fields.String(attribute="id", required=True)
    budget = fields.Method("to_euro", deserialize="to_cent")
    links = fields.List(fields.Nested(LinkSchema))
    storage = fields.Nested(StorageSchema)

    auth_type = fields.Field(load_only=True)
    role = fields.String(load_only=True, default="user")
    username = fields.String(load_only=True)
    password_hash = fields.Method(deserialize="get_password_hash", load_only=True, data_key="password")
    email = fields.String(load_only=True)
    identity_provider_id = fields.String(load_only=True)
    profile_id = fields.String(load_only=True)
    name = fields.String()

    @pre_load
    def get_id(self, in_data: dict, **kwargs: Any) -> dict:
        """Add generated user_id."""
        if "user_id" not in in_data:
            in_data["user_id"] = "us-" + str(uuid4())
        return in_data

    def get_password_hash(self, value: str) -> Optional[str]:
        """Convert password to password_hash."""
        if value:
            return pwd_context.encrypt(value)
        return None

    def to_cent(self, value: float) -> Optional[int]:
        """Convert value in euro (float) to cent (int)."""
        if value:
            return int(value * 100)
        return None

    def to_euro(self, obj: "UserSchema") -> Optional[float]:
        """Convert value in cent (int) to euro (float)."""
        if obj.budget:
            return obj.budget / 100.0
        return None


class ProfileSchema(BaseSchema):
    """Schema to store details about a profile."""

    __model__ = Profiles

    id_ = fields.String(attribute="id", data_key="id", required=True)
    name = fields.String(required=True)
    data_access = fields.String(required=True)

    @pre_load
    def add_id(self, in_data: dict, **kwargs: Any) -> dict:
        """Add generated id to profile."""
        if "id" not in in_data:
            in_data["id"] = "pr-" + str(uuid4())
        return in_data
