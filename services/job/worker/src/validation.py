''' API Payload Validation '''

from re import match
from numbers import Number
from .nodes.requests.openeo import get_single, get_all

ARG_TYPES = {
    "dict": dict,
    "array": list,
    "number": Number,
    "string": str
}

class ValidationError(Exception):
    ''' Validation Exception raises if payload is not valid. '''
    
    def __init__(self, msg=None):
        if not msg:
            msg = "The request payload is malformed or invalid."
        super(ValidationError, self).__init__(msg)
        self.code = 400

def validate_job(payload):
    ''' Ensures that the structure of the job spec is correct. '''

    if "process_graph" not in payload:
        raise ValidationError("Payload is missing a Process Graph.")
    
    validate_node(payload["process_graph"])

def validate_node(node_payload):
    ''' Validates a single node '''

    if "process_id" in node_payload:
        process_id = node_payload["process_id"]
        if process_id not in get_all("openeo", "processes", "process_id"):
            raise ValidationError("Process {0} is not available."\
                                      .format(node_payload["process_id"]))

        process_spec = get_single("openeo", "processes", process_id)

        if not "args" in node_payload:
            raise ValidationError("Process {0} is missing Process Arguments."\
                                    .format(node_payload["process_id"]))

        validate_args(process_id, node_payload["args"], process_spec["args"])

    elif "product_id" in node_payload:
        if node_payload["product_id"] not in get_all("openeo", "data", "product_id"):
            raise ValidationError("Product {0} is not available."\
                                      .format(node_payload["product_id"]))
    else:
        raise ValidationError("Node is missing a ProcessID or ProductID.")

def validate_args(process_id, args_payload, args_specs):
    ''' Validates the arguments of a node '''

    for key, value in args_specs.items():
        if key not in args_payload and args_specs[key]["required"] == True:
            raise ValidationError("Argument {0} is missing for Process {1}."\
                                        .format(key, process_id))

        validate_arg(key, args_payload[key], args_specs[key])

def validate_arg(arg_id, arg_payload, arg_specs):
    ''' Validates an argument of a node '''

    validate_type(arg_id, arg_payload, arg_specs["type"])

    if arg_specs["type"] == "string" and not match(arg_specs["regex"], arg_payload):
        raise ValidationError("String {0} does not match pattern {1}."\
                                  .format(arg_payload, arg_specs["regex"]))

    if arg_id == "imagery":
        # for collection in arg_payload:
        # TODO: Change if Core API includes collections 
        validate_node(arg_payload)

def validate_type(arg_id, arg_payload, arg_type):
    ''' Validates the type of an argument of a node '''

    if not isinstance(arg_payload, ARG_TYPES[arg_type]):
        raise ValidationError("Argument {0} is not of type {1}.".format(arg_payload, arg_type))
