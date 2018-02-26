''' API Payload Validation '''

from re import match
from service.api.api_exceptions import ValidationError

def validate_user(payload):
    ''' Ensures that the structure of a process spec is correct. '''

    if "username" not in payload:
        raise ValidationError("'username' is missing.")

    if not match(r"^\w{5,}$", payload["username"]):
        raise ValidationError("Format of 'username' is wrong. (At least 5 letters/digits)")
    
    if "email" not in payload:
        raise ValidationError("'email' is missing.")

    if not match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", payload["email"]):
        raise ValidationError("Format of 'email' is wrong.")
    
    if "admin" not in payload:
        raise ValidationError("'admin' is missing.")

    if not isinstance(payload["admin"], bool):
        raise ValidationError("Format of 'admin' is wrong (boolean)")

    if "password" not in payload:
        raise ValidationError("'password' is missing.")
    
    if not match(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$", payload["password"]):
        raise ValidationError("Format of 'password' is wrong." \
                              "(At least one upper case, at least one lower case, " \
                              "at least one digit, " \
                              "at least one special character (#?!@$%^&*-), " \
                              "minimum eight in length)")
