from flask_restful.reqparse import RequestParser

class ModelRequestParser(RequestParser):
    types = {
        "string": str,
        "str": str,
        "integer": int,
        "int": int,
        "dict": dict,
        "array": list
    }

    def __init__(self, model, location="json"):
        super().__init__(bundle_errors=True)

        if isinstance(model, list):
            for arg in model:
                choices = arg["enum"] if "enum" in arg else None
                self.add_argument(
                            arg["name"], 
                            type=self.types.get(arg["type"], str), 
                            default=arg["default"],
                            required=arg["required"], 
                            choices=choices, 
                            location=location,
                            help=arg["description"])
        else:    
            if hasattr(model, "properties"):
                for key, value in model.properties.items():
                    required = True if hasattr(model, "required") and key in model.required else False
                    choices = model.enum if hasattr(model, "enum") else None
                    type = self.types.get(value["type"], str) if isinstance(value, dict) else dict

                    self.add_argument(
                        key, 
                        type=type, 
                        required=required, 
                        choices=choices, 
                        location=location)
