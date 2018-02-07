''' Validates the input payload '''

from numbers import Number
from re import match
from requests import get
from service.src.processes import get_available_processes, get_process_spec

ARG_TYPES = {
    "array": list,
    "number": Number,
    "string": str
}

SENTINEL_PRODUCTS = [
    "S2_L2A_T32TPS_20M"
]


class ValidationException(Exception):
    ''' Validation Exception raises if the payload validation fails. '''
    pass

def validate_payload(payload):
    ''' Initialisation of payload validation '''

    if "process_graph" not in payload:
        raise ValidationException("Payload is missing a Process Graph.")

    validate_node(payload["process_graph"])

def validate_node(node_payload):
    ''' Validates a single node '''

    if "process_id" in node_payload:
        if node_payload["process_id"] not in get_available_processes():
            raise ValidationException("Process {0} is not available."\
                                      .format(node_payload["process_id"]))

        process_spec = get_process_spec(node_payload["process_id"])

        if not "args" in node_payload:
            raise ValidationException("Process {0} is missing Process Arguments."\
                                    .format(node_payload["process_id"]))

        validate_args(node_payload["process_id"], node_payload["args"], process_spec["args"])

    elif "product_id" in node_payload:
        if node_payload["product_id"] not in get_products():
            raise ValidationException("Product {0} is not available."\
                                      .format(node_payload["product_id"]))
    else:
        raise ValidationException("Node is missing a ProcessID or ProductID.")

def validate_args(process_id, args_payload, args_specs):
    ''' Validates the arguments of a node '''

    for key, value in args_specs.items():
        if key not in args_payload and args_specs[key]["required"] == True:
            raise ValidationException("Argument {0} is missing for Process {1}."\
                                        .format(key, process_id))

        validate_arg(key, args_payload[key], args_specs[key])

def validate_arg(arg_id, arg_payload, arg_specs):
    ''' Validates an argument of a node '''

    validate_type(arg_id, arg_payload, arg_specs["type"])

    if arg_specs["type"] == "string" and not match(arg_specs["regex"], arg_payload):
        raise ValidationException("String {0} does not match pattern {1}."\
                                  .format(arg_payload, arg_specs["regex"]))

    if arg_id == "collections":
        for collection in arg_payload:
            validate_node(collection)

def validate_type(arg_id, arg_payload, arg_type):
    ''' Validates the type of an argument of a node '''

    if not isinstance(arg_payload, ARG_TYPES[arg_type]):
        raise ValidationException("Argument {0} is not of type {1}.".format(arg_payload, arg_type))
