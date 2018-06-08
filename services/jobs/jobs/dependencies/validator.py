''' API Payload Validation '''

from re import match
from numbers import Number
from nameko.extensions import DependencyProvider

from ..exceptions import BadRequest


class ValidatorWrapper:
    def __init__(self):
        self.arg_types = {
            "dict": dict,
            "array": list,
            "number": Number,
            "string": str
        }
    
    def update_datasets(self, processes, products):
        self.processes = processes
        self.products = products

    def validate_node(self, node_payload):
        ''' Validates a single node '''

        if "process_id" in node_payload:
            process_id = node_payload["process_id"]

            if not "args" in node_payload:
                raise BadRequest("Process {0} is missing Process Arguments.".format(process_id))
            
            process_spec = None
            for process in self.processes:
                if process['process_id'] == process_id:
                    process_spec = process
                    break

            if not process_spec:
                raise BadRequest("Process {0} is not available.".format(node_payload["process_id"]))

            self.validate_args(process_id, node_payload["args"], process_spec["args"])

        elif "product_id" in node_payload:
            if not any(p['product_id'] == node_payload["product_id"] for p in self.products):
                raise BadRequest("Product {0} is not available.".format(node_payload["product_id"]))
        else:
            raise BadRequest("Node is missing a ProcessID or ProductID.")

    def validate_args(self, process_id, args_payload, args_specs):
        ''' Validates the arguments of a node '''

        for key, value in args_specs.items():
            if key not in args_payload and args_specs[key]["required"] == True:
                raise BadRequest("Argument {0} is missing for Process {1}.".format(key, process_id))

            self.validate_arg(key, args_payload[key], args_specs[key])

    def validate_arg(self, arg_id, arg_payload, arg_specs):
        ''' Validates an argument of a node '''

        self.validate_type(arg_id, arg_payload, arg_specs["type"])

        if arg_specs["type"] == "string" and not match(arg_specs["regex"], arg_payload):
            raise BadRequest("String {0} does not match pattern {1}.".format(arg_payload, arg_specs["regex"]))

        if arg_id == "imagery":
            # TODO: Change if Core API includes collections (e.g. for collection in arg_payload:)
            self.validate_node(arg_payload)

    def validate_type(self, arg_id, arg_payload, arg_type):
        ''' Validates the type of an argument of a node '''

        if not isinstance(arg_payload, self.arg_types[arg_type]):
            raise BadRequest("Argument {0} is not of type {1}.".format(arg_payload, arg_type))


class Validator(DependencyProvider):
    def get_dependency(self, worker_ctx):
        return ValidatorWrapper()
