"""Test api functionality related to users."""
from typing import Callable

import pytest
from sqlalchemy import Column
from sqlalchemy.orm import Session

from users.models import AuthType, Profiles, Users
from .utils import InputDictGenerator, RandomDbAdder, get_ref_user, get_user_service


class TestUser:
    """Test functionality to add, delete and get a user."""

    def test_add_oidc(self, db_session: Session) -> None:
        """Check a proper oidc user can be added."""
        user_service = get_user_service(db_session)
        identity_provider = RandomDbAdder().random_identity_provider(db_session)
        profile = RandomDbAdder().random_profile(db_session)
        oidc_user_dict = InputDictGenerator().random_oidc_user(profile.name, identity_provider.id_openeo)

        response = user_service.add_user(**oidc_user_dict)

        assert response == {
            "status": "success",
            "code": 200,
            "data": {"message": f"User '{oidc_user_dict['email']}' successfully added to database."},
        }
        actual_user = db_session.query(Users).filter_by(email=oidc_user_dict['email']).one()
        assert actual_user.id.startswith("us-")
        assert actual_user.auth_type == AuthType.oidc
        assert actual_user.role == "user"
        assert actual_user.username is None
        assert actual_user.password_hash is None
        assert actual_user.email == oidc_user_dict["email"]
        assert actual_user.identity_provider_id == identity_provider.id
        assert actual_user.profile_id == profile.id
        assert actual_user.budget is None
        assert actual_user.name is None

    def test_add_basic(self, db_session: Session) -> None:
        """Check a proper basic user can be added."""
        user_service = get_user_service(db_session)
        profile = RandomDbAdder().random_profile(db_session)
        basic_user_dict = InputDictGenerator().random_basic_user(profile.name)

        response = user_service.add_user(**basic_user_dict)

        assert response == {
            "status": "success",
            "code": 200,
            "data": {"message": f"User '{basic_user_dict['username']}' successfully added to database."},
        }
        actual_user = db_session.query(Users).filter_by(username=basic_user_dict["username"]).one()
        assert actual_user.id.startswith("us-")
        assert actual_user.auth_type == AuthType.basic
        assert actual_user.role == "user"
        assert actual_user.username == basic_user_dict["username"]
        assert actual_user.password_hash != basic_user_dict["password"]
        assert actual_user.email is None
        assert actual_user.identity_provider_id is None
        assert actual_user.profile_id == profile.id
        assert actual_user.budget is None
        assert actual_user.name is None

    @pytest.mark.parametrize(("get_user", "attribute", "db_column"), (
        (RandomDbAdder().random_basic_user, "username", Users.username),
        (RandomDbAdder().random_oidc_user, "email", Users.email),
    ))
    def test_delete(self, db_session: Session, get_user: Callable, attribute: str, db_column: Column) -> None:
        """Check a basic and oidc user can be deleted.

        Args:
            db_session: Database session used to connected to the database.
            get_user: Function to add and retrieve a user (basic or oidc) to the database.
            attribute: Name of the unique identifier key for the user. Either username for basic users or email for
                oidc users.
            db_column: Equivalent to the attribute key but the corresponding database column.
                (Users.username or Users.email)
        """
        user_service = get_user_service(db_session)
        user = get_user(db_session)
        assert db_session.query(Users).filter(db_column == getattr(user, attribute)).one()

        response = user_service.delete_user(**{attribute: getattr(user, attribute)})

        assert response == {
            "status": "success",
            "code": 200,
            "data": {'message': f"User '{getattr(user, attribute)}' successfully removed from database."},
        }
        assert len(db_session.query(Users).filter(db_column == getattr(user, attribute)).all()) == 0

    @pytest.mark.parametrize(("get_user", "attribute", "db_column"), (
        (RandomDbAdder().random_basic_user, "username", Users.username),
        (RandomDbAdder().random_oidc_user, "email", Users.email)
    ))
    def test_get(self, db_session: Session, get_user: Callable, attribute: str, db_column: Column) -> None:
        """Check basic and oidc user are returned in the correct format.

        Args:
            db_session: Database session used to connected to the database.
            get_user: Function to add and retrieve a user (basic or oidc) to the database.
            attribute: Name of the unique identifier key for the user. Either username for basic users or email for
                oidc users.
            db_column: Equivalent to the attribute key but the corresponding database column.
                (Users.username or Users.email)
        """
        user_service = get_user_service(db_session)
        user = get_user(db_session)
        assert db_session.query(Users).filter(db_column == getattr(user, attribute)).one()

        response = user_service.get_user_info({"id": user.id})

        assert response == {
            "status": "success",
            "code": 200,
            "data": {
                "user_id": user.id,
            },
        }

    @pytest.mark.parametrize(("get_user", "attribute", "db_column", "entity_attr", "entity_column"), (
        (RandomDbAdder().random_basic_user, "username", Users.username, "id", Users.id),
        (RandomDbAdder().random_oidc_user, "email", Users.email, "id", Users.id),
        (RandomDbAdder().random_basic_user, "username", Users.username, "email", Users.email),
        (RandomDbAdder().random_oidc_user, "email", Users.email, "email", Users.email),
        (RandomDbAdder().random_basic_user, "username", Users.username, "username", Users.username),
        (RandomDbAdder().random_oidc_user, "email", Users.email, "username", Users.username),
    ))
    def test_user_entity_by(self, db_session: Session, get_user: Callable, attribute: str, db_column: Column,
                            entity_attr: str, entity_column: Column) -> None:
        """Check the get_entity_by rpc functions all return a correct user entity dict.

        Args:
            db_session: Database session to connect to the DB.
            get_user: Function from the .utils which inserts (into the DB) and returns a new user.
            attribute: Name of the unique identifier key for the user. Either username for basic users or email for
                oidc users.
            db_column: Equivalent to the attribute key but the corresponding database column.
                (Users.username or Users.email)
            entity_attr: Name of the key used to get the user entity. (id, username, email)
            entity_column: Equivalent to the entity_attr to the corresponding database column.
                (Users.id, Users.email, Users.username)
        """
        user_service = get_user_service(db_session)
        user = get_user(db_session)
        profile = db_session.query(Profiles).filter_by(id=user.profile_id).first()
        assert db_session.query(Users).filter(db_column == getattr(user, attribute)).one()

        entity_func_map = {
            "id": user_service.get_user_entity_by_id,
            "email": user_service.get_user_entity_by_email,
            "username": user_service.get_user_entity_by_username,
        }

        response = entity_func_map[entity_attr](getattr(user, entity_attr))

        assert response == get_ref_user(user, profile)
