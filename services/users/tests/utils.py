"""Utility functions used in the tests."""
import random
import string
from datetime import datetime
from typing import Dict, List, Optional, Union
from uuid import uuid4

from nameko.testing.services import worker_factory
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy.orm import Session

from users.models import AuthType, IdentityProviders, Profiles, Users
from users.service import UsersService


def name_generator(size: int = 6, chars: str = string.ascii_uppercase + string.digits) -> str:
    """Get a random name."""
    return ''.join(random.choice(chars) for _ in range(size))  # noqa s311 - no security/cryptographic purposes - tests


def id_generator() -> str:
    """Get a random id."""
    return str(uuid4())


class DbAdder:
    """Utility functions to add records to Users DB."""

    def identity_provider(self, db_session: Session, id_: str, id_openeo: str, issuer_url: str, scopes: str, title: str,
                          description: Optional[str] = None) -> IdentityProviders:
        """Add an identity provider to the database."""
        identity_provider = IdentityProviders(
            id=id_,
            id_openeo=id_openeo,
            issuer_url=issuer_url,
            scopes=scopes,
            title=title,
            description=description
        )
        db_session.add(identity_provider)
        db_session.commit()
        return identity_provider

    def profile(self, db_session: Session, id_: str, name: str, data_access: str) -> Profiles:
        """Add a user profile to the database."""
        profile = Profiles(
            id=id_,
            name=name,
            data_access=data_access,
        )
        db_session.add(profile)
        db_session.commit()
        return profile

    def user(self, db_session: Session, id_: str, auth_type: AuthType, profile_id: str, role: Optional[str] = "user",
             username: Optional[str] = None, password_hash: Optional[str] = None, email: Optional[str] = None,
             identity_provider_id: Optional[str] = None, budget: Optional[int] = None, name: Optional[str] = None,
             created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None) \
            -> Users:
        """Add a user to the database and return it."""
        user = Users(
            id=id_,
            auth_type=auth_type,
            role=role,
            username=username,
            password_hash=password_hash,
            email=email,
            identity_provider_id=identity_provider_id,
            profile_id=profile_id,
            budget=budget,
            name=name,
            created_at=created_at if created_at else datetime.utcnow(),
            updated_at=updated_at if updated_at else datetime.utcnow(),
        )
        db_session.add(user)
        db_session.commit()
        return user


class RandomDbAdder:
    """Utility functions to add random instances to the database."""

    db_add = DbAdder()

    def random_identity_provider(self, db_session: Session) -> IdentityProviders:
        """Add a random identity provider to the database and return its id_openeo."""
        return self.db_add.identity_provider(
            db_session=db_session,
            id_=f"ip-{id_generator()}",
            id_openeo=name_generator(),
            issuer_url="https://accounts.random.com",
            scopes="openid,email",
            title=name_generator(),
        )

    def random_profile(self, db_session: Session) -> Profiles:
        """Add a random basic profile and return it."""
        return self.db_add.profile(
            db_session=db_session,
            id_=f"pr-{id_generator()}",
            name=name_generator(),
            data_access=f"{name_generator()},{name_generator()}",
        )

    def random_basic_user(self, db_session: Session) -> Users:
        """Add a random profile and basic user and return the user object."""
        profile = self.random_profile(db_session)
        password = name_generator()
        return self.db_add.user(
            db_session=db_session,
            id_=f"us-{id_generator()}",
            auth_type=AuthType.basic,
            username=name_generator(),
            password_hash=pwd_context.encrypt(password),
            profile_id=profile.id,
        )

    def random_oidc_user(self, db_session: Session) -> Users:
        """Add a random profile, identity_provider and oidc user and return the user object."""
        profile = self.random_profile(db_session)
        identity_provider = self.random_identity_provider(db_session)
        return self.db_add.user(
            db_session=db_session,
            id_=f"us-{id_generator()}",
            auth_type=AuthType.oidc,
            email=f"{name_generator()}@sample.com",
            identity_provider_id=identity_provider.id,
            profile_id=profile.id,
        )


class InputDictGenerator:
    """Utility functions to get random service input dicts."""

    def random_basic_user(self, profile_name: str) -> Dict[str, str]:
        """Return random input dict to add a basic user."""
        return {
            "username": name_generator(),
            "password": name_generator(),
            "profile": profile_name,
        }

    def random_oidc_user(self, profile_name: str, identity_provider_id_openeo: str) -> Dict[str, str]:
        """Return random input dict to add an oidc user."""
        return {
            "email": f"{name_generator()}@user.com",
            "identity_provider": identity_provider_id_openeo,
            "profile": profile_name,
        }

    def random_profile(self) -> Dict[str, str]:
        """Return random input dict to add a profile."""
        return {
            "name": name_generator(),
            "data_access": f"{name_generator()},{name_generator()}",
        }

    def random_identity_provider(self) -> Dict[str, Union[str, List[str]]]:
        """Return random identity provider dict to add an identity provider."""
        return {
            "id": name_generator(),
            "issuer": f"https://accounts.{name_generator()}.com",
            "scopes": ["openid", "email"],
            "title": name_generator(),
        }


def get_user_service(db_session: Session) -> UsersService:
    """Return a mocked user service."""
    return worker_factory(UsersService, db=db_session)
