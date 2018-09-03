''' API Payload Validation '''

from re import match
from numbers import Number
from nameko.extensions import DependencyProvider
from jsonschema import validate, ValidationError


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

        if not "process_id" in node_payload:
            raise ValidationError("Node is missing a ProcessID or ProductID.")

        process_id = node_payload["process_id"]
        process_spec = [process for process in self.processes if process['name'] == process_id]

        if len(process_spec) != 1:
            raise ValidationError("Process '{0}' is not available.".format(node_payload["process_id"]))

        self.validate_args(process_id, node_payload, process_spec[0]["parameters"])

    def validate_args(self, process_id, args_payload, args_specs):
        ''' Validates the arguments of a node '''

        for arg_id, arg_spec in args_specs.items():
            # Check if not argument is another node
            if arg_id == "imagery": 
                self.validate_node(args_payload[arg_id])
                continue

            # Check if product is available at the back-end
            if arg_id == "data_id" and not any(p['data_id'] == args_payload[arg_id] for p in self.products):
                raise ValidationError("Product '{0}' is not available.".format(args_payload[arg_id]))

            # Validate argument using JSON Schema
            if arg_id in args_payload:
                validate(args_payload[arg_id], arg_spec["schema"])
                continue

            # Raise error if argument is required but missing.
            if args_specs[arg_id]["required"] == True:
                raise ValidationError("Argument '{0}' is missing for Process '{1}'.".format(arg_id, process_id))


class Validator(DependencyProvider):
    def get_dependency(self, worker_ctx):
        return ValidatorWrapper()
