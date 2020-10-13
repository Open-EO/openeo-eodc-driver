from datetime import datetime
from os import environ

from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from users.models import IdentityProviders, Profiles, Users


def get_password_hash(password: str) -> str:
    return pwd_context.encrypt(password)


def get_db_session(db_url: str) -> Session:
    engine = create_engine(db_url)
    session_maker = sessionmaker(bind=engine)
    return session_maker()


def main():
    db_url = f"postgresql://{environ.get('OEO_DB_USERNAME')}:{environ.get('OEO_DB_PASSWORD')}" \
             f"@{environ.get('OEO_DB_HOST')}:{environ.get('OEO_DB_PORT')}/{environ.get('OEO_DB_NAME')}"
    print(db_url)
    session = get_db_session(db_url)

    profile_1 = Profiles(
        id='pr-19144eb0-ecde-4821-bc8b-714877203c85',
        name=environ.get("PROFILE_1_NAME"),
        data_access=environ.get("PROFILE_1_DATA_ACCESS"),
    )
    profile_2 = Profiles(
        id="pr-c36177bf-b544-473f-a9ee-56de7cece055",
        name=environ.get("PROFILE_2_NAME"),
        data_access=environ.get("PROFILE_2_DATA_ACCESS"),
    )
    identity_provider = IdentityProviders(
        id="ip-c462aab2-fdbc-4e56-9aa1-67a437275f5e",
        id_openeo=environ.get("ID_PROVIDER_ID"),
        issuer_url=environ.get("ID_PROVIDER_ISSUER_URL"),
        scopes="openid,email",
        title=environ.get("ID_PROVIDER_TITLE"),
        description=environ.get("ID_PROVIDER_DESCRIPTION"),
    )
    basic_user = Users(
        id="us-9005284b-3a76-444f-96a2-df0464d0e73c",
        auth_type="basic",
        role="admin",
        username=environ.get("USER_BASIC_ADMIN"),
        password_hash=get_password_hash(environ.get("PASSWORD_BASIC_ADMIN")),
        profile_id=profile_1.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    oidc_user = Users(
            id="us-915688b5-9869-417b-92a2-463ef0a68b45",
            auth_type="oidc",
            role="admin",
            email=environ.get("EMAIL_OIDC_ADMIN"),
            profile_id=profile_1.id,
            identity_provider_id=identity_provider.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    session.add(profile_1)
    session.add(profile_2)
    session.add(identity_provider)
    session.add(basic_user)
    session.add(oidc_user)
    session.commit()


if __name__ == '__main__':
    main()
