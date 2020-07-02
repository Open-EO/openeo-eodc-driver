from typing import Any, Dict

from .models import Profiles, Users


def db_to_dict_user(db_user: Users, db_profile: Profiles) -> Dict[str, Any]:
    return {
        "id": db_user.id,
        "role": db_user.role,
        "auth_type": str(db_user.auth_type),
        "username": db_user.username,
        "email": db_user.email,
        "profile": {
            "name": db_profile.name,
            "data_access": db_profile.data_access.split(",")
        },
        "budget": db_user.budget,
        "created_at": db_user.created_at,
        "updated_at": db_user.updated_at,
    }
