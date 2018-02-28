''' API Payload Validation '''

from re import match
from service.api.api_exceptions import ValidationError

def validate_process(payload):
    ''' Ensures that the structure of a process spec is correct. '''

    if "process_id" not in payload:
        raise ValidationError("Process ID is missing.")

    if not match(r"^([a-z]|[0-9]|-|_)*$", payload["process_id"]):
        raise ValidationError("Format of Process ID is wrong ([a-z] | 0-9 | - | _ ).")

    if "description" not in payload:
        raise ValidationError("Description is missing.")

    if "type" not in payload:
        raise ValidationError("Process type is missing.")

    if not match(r"^(filter|operation)$", payload["type"]):
        raise ValidationError("Format of process type is wrong.")

    if payload["type"] == "operation":
        if not "git_uri" in payload:
            raise ValidationError("Git URI is missing.")

        if not match(r"(^https:\/\/(\w|\d|.|\/|-|_)+.git$|^git@(\w|\d|.|\/|-|_)+.git$)", payload["git_uri"]):
            raise ValidationError("Format of Git URI is wrong.")

        if "git_ref" not in payload:
            raise ValidationError("Git reference is missing.")

        if not match(r"^(\w|\d|-|_)+$", payload["git_ref"]):
            raise ValidationError("Format of Git Reference is wrong.")

        if "git_dir" in payload:
            if not match(r"^(\w|\/|\_|\-|\.)*$", payload["git_ref"]):
                raise ValidationError("Format of Git Dir is wrong.")

    if "args" not in payload:
        raise ValidationError("Process Arguments are missing.")

    for key, value in payload["args"].items():
        arg = payload["args"][key]

        if "description" not in arg:
            raise ValidationError("Description for argument {0} is missing.".format(key))

        if "type" not in arg:
            raise ValidationError("Type for argument {0} is missing.".format(key))

        if not match(r"^(dict|array|number|string)$", arg["type"]):
            raise ValidationError("Format of argument {0} is wrong.".format(key))

        if arg["type"] == "string" and "regex" not in arg:
            raise ValidationError("RegEx for argument {0} is missing.".format(key))

        if "required" not in arg:
            raise ValidationError("Requirement for argument {0} is missing.".format(key))
