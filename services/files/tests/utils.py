"""Utility methods used in the tests."""
from typing import Any, Dict


def create_user(user_id: str) -> Dict[str, Any]:
    """Return a user object defined by a user_id."""
    return {
        "id": user_id
    }
