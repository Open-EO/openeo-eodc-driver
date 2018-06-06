from flask_restful_swagger_2 import Schema


class arg_set(Schema):
    type = "object"
    additionalProperties: True
    description = (
        "Defines an object schema for a collection of uniquely named arguments"
        "(argument set) as input to processes.")


class process_description(Schema):
    type = "object"
    description = (
        "A process is a operation or filter that can be referenced in a "
        "process graph.")
    required = ["process_id", "description", "process_type"]
    properties = {
        "process_id": {
            "type": "string",
            "description": "The unique identifier of the process.",
        },
        "description": {
            "type": "string",
            "description": "A short and concise description of what the process does and how the output looks like.",
        },
        "process_type": {
            "type": "string",
            "enum": ["operation", "filter"],
            "description": "The type of the process ('operation' or 'filter').",
        },
        "link": {
            "type": "string",
            "description": "Reference to an external process definition if the process has been defined over different back ends within OpenEO.",
        },
        "args": arg_set,
        "git_uri": {
            "type": "string",
            "description": "The URI to the Git repository from which the code is fetched.",
        },
        "git_ref": {
            "type": "string",
            "description": "The branch of the Git repository from which the code is fetched.",
        },
        "git_dir": {
            "type": "string",
            "description": "The directory of the Git repository from which the code is fetched.",
        }
    }
    example = {
        "process_id": "band_arithmetic",
        "process_type": "operation",
        "description": "Perform basic arithmetic expressions on individual pixel and their band values.",
        "args": {
            "imagery": {
                "description": "input image or image collection",
                "required": "true"
            },
            "expr": {
                "description": (
                    "expressions as array, the result will have as many bands as the "
                    "number of given expressions.")
            }
        },
        "git_uri": "https://github.com/me/band_arithmetic",
        "git_ref": "master",
        "git_dir": "."
    }


class process_graph(Schema):
    type = "object"
    description = (
        "A process graph defines an executable process, i.e. one process or a"
        "combination of chained processes including specific arguments.")
    required = ["process_id", "args"]
    properties = {
        "process_id": {
            "type": "string",
            "description": "The unique identifier of the process."
        },
        "args": arg_set
    }
    example = {
        "process_id": "min_time",
        "args": {
            "imagery": {
                "process_id": "NDVI",
                "args": {
                    "imagery": {
                        "process_id": "filter_daterange",
                        "args": {
                            "imagery": {
                                "process_id": "filter_bbox",
                                "args": {
                                    "imagery": {
                                        "product_id": "s2a_prd_msil1c"
                                    },
                                    "left": 16.341818660,
                                    "right": 16.431082576,
                                    "top": 48.243246389,
                                    "bottom": 48.202989476,
                                    "srs": "EPSG:4326"
                                }
                            },
                            "from": "2018-01-01",
                            "to": "2018-01-05"
                        }
                    },
                    "red": "B04",
                    "nir": "B8A"
                }
            }
        }
    }


class output(Schema):
    type = "object"
    description = (
        "Output format to be used. Supported formats and options can be retrieved "
        "using the `GET /capabilities/output_formats` endpoint.")
    required = ["format"]
    properties = {
        "format": {
            "type": "string",
            "description": "One of the supported output formats."
        }
    }
    additionalProperties: True
    example = {
        "format": "GTiff",
        "tiles": "true",
        "compress": "jpeg",
        "photometric": "YCBCR",
        "jpeg_quality": "80"
    }

# TODO: Improve


class job_val(Schema):
    type = "object"
    description = (
        "Specifies the job details, e.g. the process graph and optionally the output format. The output format might be also specified later during download and is not necessary for web services at all."
    )
    required = ["format"]
    properties = {
        "process_graph": {
            "type": "dict",
            "description": "A process graph defines an executable process, i.e. one process or a combination of chained processes including specific arguments."
        },
        "output": {
            "type": "dict",
            "description": "Output format to be used. Supported formats and options can be retrieved using the GET /capabilities/output_formats endpoint."
        }
    }


class password(Schema):
    type = "object"
    description = "Password to be used for the newly created user account."
    required = ["password"]
    properties = {
        "password": {
            "type": "string",
            "description": "Password to be used for the newly created user account."
        }
    }
    example = {
        "password": "mySecr3tP@ssword"
    }
