from os import environ

from gateway.dependencies.response import APIException


class AuthService:
    """
    Handle User Authentication either with Basic or OIDC.
    """

    def get_user_info(self, user_id: str) -> dict:
        """Returns info about the (logged in) user.

        Returns:
            Dict -- 200 HTTP code
        """
        return {
            "status": "success",
            "code": 200,
            "data": {"user_id": user_id},
        }

    def send_openid_connect_discovery(self) -> dict:
        """Redirects to the OpenID Connect discovery document.

        Returns:
            Dict -- Redirect to the OpenID Connect discovery document
        """

        return {
            "status": "redirect",
            "url": environ.get("OPENID_DISCOVERY"),
        }

    def get_basic_token(self, username: str, password: str) -> dict:
        """
        Generate token for basic user.

        Returns:
            Dict -- User_id with access token
        """
        from gateway.users.repository import db,  Users

        user = db.session.query(Users).filter(Users.username == username).scalar()
        if user.verify_password(password):

            out_data = {}
            out_data["user_id"], out_data["token"] = user.generate_auth_token(expiration=600)
            # support multiple versions: v0.4.2 needs "token", draft version needs "access_token"
            out_data["access_token"] = out_data["token"]
            return {
                "status": "success",
                "code": 200,
                "data": out_data,
            }
        else:
            raise APIException(
                msg=f"Incorrect credentials for user {username}.",
                code=401,
                service="gateway",
                internal=False,
            )
