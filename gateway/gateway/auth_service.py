from os import environ
from flask.wrappers import Response

class AuthService:
    """
    
    """
    
    def __init__(self, response_parser):
        self._res = response_parser # this comes from the Gateway instance


    def get_user_info(self, user_id: str) -> Response:
        """Returns info about the (logged in) user.

        Returns:
            Response -- 200 HTTP code
        """
        user_info = {}
        user_info['user_id'] = user_id

        return self._res.parse({"code": 200, "data": user_info})
        
    
    def send_openid_connect_discovery(self) -> Response:
        """Redirects to the OpenID Connect discovery document.

        Returns:
            Response -- Redirect to the OpenID Connect discovery document
        """

        return self._res.redirect(environ.get("OPENID_DISCOVERY"))
        
    
    def get_basic_token(self, username: str, password: str) -> Response:
        """
        Generate token for basic user.
        """

        from gateway.users.repository import db,  Users
        
        user = db.session.query(Users).filter(Users.username == username).scalar()
        if user.verify_password(password):
            
            out_data = {}
            out_data['user_id'], out_data['token'] = user.generate_auth_token(expiration=600)
            # support multiple versions: v0.4.2 needs 'token', draft version needs 'access_token'
            out_data['access_token'] = out_data['token']
            
            return self._res.parse({"code": 200, "data": out_data})
            
        else:
            # TODO Raise proper error
            return self._res.parse({"code": 400, "data": {'message': f'Incorrect credentials for user {username}.'}})
