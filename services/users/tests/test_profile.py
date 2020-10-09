"""Test api functionality related to user profiles."""
from sqlalchemy.orm import Session

from users.models import Profiles
from .utils import InputDictGenerator, RandomDbAdder, get_user_service


class TestProfile:
    """Test functionality to add and delete a user profile."""

    def test_add(self, db_session: Session) -> None:
        """Check a proper profile can be added."""
        user_service = get_user_service(db_session)
        profile_dict = InputDictGenerator().random_profile()

        response = user_service.add_user_profile(**profile_dict)

        assert response == {
            "status": "success",
            "code": 200,
            "data": {'message': f"Profile '{profile_dict['name']}' added to database."}
        }
        assert db_session.query(Profiles).filter_by(name=profile_dict["name"]).one()

    def test_delete(self, db_session: Session) -> None:
        """Check a user profile can be deleted."""
        user_service = get_user_service(db_session)
        profile = RandomDbAdder().random_profile(db_session)
        assert db_session.query(Profiles).filter_by(name=profile.name).one()

        response = user_service.delete_user_profile(**{"name": profile.name})

        assert response == {
            "status": "success",
            "code": 200,
            "data": {'message': f"Profile '{profile.name}' removed from database."}
        }
        assert len(db_session.query(Profiles).filter_by(name=profile.name).all()) == 0
