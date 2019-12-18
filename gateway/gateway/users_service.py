

from flask.wrappers import Response
from gateway.users.repository import insert_users, insert_identity_provider


class UsersService:
    """
    
    """

    def __init__(self, response_parser):
        self._res = response_parser # this comes from the Gateway instance


    def add_user(self, **kwargs) -> Response:
        """
        Add Basic or OIDC user to database.
        """
                
        if 'role' not in kwargs:
            kwargs['role'] = 'user'

        if 'username' in kwargs and 'password' in kwargs and 'profile_name' in kwargs:
            insert_users(auth_type='basic', profile_name=kwargs['profile_name'], role=kwargs['role'], username=kwargs['username'], password=kwargs['password'])
            out_field = kwargs['username']
        elif 'email' in kwargs and 'identity_provider' in kwargs and 'profile_name' in kwargs:
            insert_users(auth_type='oidc', profile_name=kwargs['profile_name'], role=kwargs['role'], email=kwargs['email'], identity_provider=kwargs['identity_provider'])
            out_field = kwargs['email']
                
        out_data = {}
        out_data['message'] = f"User '{out_field}' added to database."
    
        return self._res.parse({"code": 200, "data": out_data})
        
    
    def add_identity_provider(self, id_openeo: str, issuer_url: str, scopes: list, title: str, description: str = None) -> Response:
        """
        Add Identity provider to database for OIDC authentication.
        """
        
        insert_identity_provider(id_openeo=id_openeo, issuer_url=issuer_url, scopes=['openid', 'email'], title=title, description=description)
        out_data = {}
        out_data['message'] = f"Identity provider '{id_openeo}' added to database."
    
        return self._res.parse({"code": 200, "data": out_data})
