"""Test api functionality related to identity providers."""
from sqlalchemy.orm import Session

from users.models import IdentityProviders
from .utils import InputDictGenerator, RandomDbAdder, get_user_service


class TestIdentityProvider:
    """Test functionality for add, delete and get identity providers."""

    def test_add(self, db_session: Session) -> None:
        """Check an identity provider can be added."""
        user_service = get_user_service(db_session)
        identity_provider_dict = InputDictGenerator().random_identity_provider()

        response = user_service.add_identity_provider(**identity_provider_dict)

        assert response == {
            "status": "success",
            "code": 200,
            "data": {'message': f"Identity provider '{identity_provider_dict['id']}' added to database."}
        }
        assert db_session.query(IdentityProviders).filter_by(id_openeo=identity_provider_dict["id"]).one()

    def test_delete(self, db_session: Session) -> None:
        """Check an identity provider can be deleted."""
        user_service = get_user_service(db_session)
        identity_provider = RandomDbAdder().random_identity_provider(db_session)

        response = user_service.delete_identity_provider(**{"id": identity_provider.id_openeo})

        assert response == {
            "status": "success",
            "code": 200,
            "data": {"message": f"Identity provider {identity_provider.id_openeo} successfully deleted."}
        }
        assert len(db_session.query(IdentityProviders).filter_by(id_openeo=identity_provider.id_openeo).all()) == 0

    def test_get(self, db_session: Session) -> None:
        """Check the list of identity providers is returned in the correct format."""
        user_service = get_user_service(db_session)
        num = 3
        identity_providers = [RandomDbAdder().random_identity_provider(db_session) for _ in range(num)]
        assert len(db_session.query(IdentityProviders).all()) == 3

        response = user_service.get_oidc_providers()

        assert response == {
            "status": "success",
            "code": 200,
            "data": {
                "providers": [
                    {
                        "id": id_prov.id_openeo,
                        "issuer": id_prov.issuer_url,
                        "scopes": id_prov.scopes.split(","),
                        "title": id_prov.title,
                    } for id_prov in identity_providers
                ]
            }
        }
