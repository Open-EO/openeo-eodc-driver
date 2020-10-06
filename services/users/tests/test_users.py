"""Test api functionality related to users."""
from typing import Callable

import pytest
from sqlalchemy import Column
from sqlalchemy.orm import Session

from users.models import AuthType, Users
from .utils import InputDictGenerator, RandomDbAdder, get_user_service


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

    @pytest.mark.parametrize("get_user",
                             (RandomDbAdder().random_basic_user, RandomDbAdder().random_oidc_user))
    def test_get(self, db_session: Session, get_user: Callable) -> None:
        """Check basic and oidc user are returned in the correct format.

        Args:
            db_session: Database session used to connected to the database.
            get_user: Function to add and retrieve a user (basic or oidc) to the database.
        """
        user_service = get_user_service(db_session)
        user = get_user(db_session)
        assert db_session.query(Users).filter_by(email=user.email).one()

        response = user_service.get_user_info({"id": user.id})

        assert response == {
            "status": "success",
            "code": 200,
            "data": {
                "user_id": user.id,
            },
        }
