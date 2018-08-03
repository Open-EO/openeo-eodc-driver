from .models import process_description, process_graph, output, password
# AUTH
password_body = {
    "name": "password",
    "in": "body",
    "description": "Password to be used for the newly created user account.",
    "required": True,
    "schema": password
}

# PROCESS
process_id = {
    "name": "process_id",
    "in": "path",
    "type": "string",
    "description": "process identifier string such as `NDVI`",
    "required": True
}

process_body = {
    "name": "process",
    "in": "body",
    "description": ("Specifies the process details."),
    "schema": process_description
}

# DATA
product_id = {
    "name": "product_id",
    "in": "path",
    "type": "string",
    "description": "product identifier string such as `MOD18Q1`",
    "required": True
}

qtype = {
    "name": "qtype",
    "description": "Object of interest (products, records, file_paths)",
    "required": False,
    "enum": [
        "products",
        "product_details",
        "full",
        "short",
        "file_paths"
    ],
    "default": "products",
    "type": "string",
    "in": "query"
}

qname = {
    "name": "qname",
    "description": "String expression to search available datasets/processes by name.",
    "required": False,
    "type": "string",
    "in": "query",
    "default": ""
}

qgeom = {
    "name": "qgeom",
    "description": "WKT polygon to search for available datasets that spatially intersect with the polygon.",
    "required": False,
    "type": "string",
    "in": "query",
    "default": ""
}

qstartdate = {
    "name": "qstartdate",
    "description": "ISO 8601 date/time string to find datasets with any data acquired after the given date/time.",
    "required": False,
    "type": "string",
    "in": "query",
    "default": ""
}

qenddate = {
    "name": "qenddate",
    "description": "ISO 8601 date/time string to find datasets with any data acquired before the given date/time.",
    "required": False,
    "type": "string",
    "in": "query",
    "default": ""
}

# JOB
job_body = {
    "name": "job",
    "in": "body",
    "description": (
        "Specifies the job details, e.g. the process graph and _optionally_"
        "the output format. The output format might be also specified later "
        "during download and is not necessary for web services at all."
    ),
    "schema": {
        "type": "object",
        "properties": {
            "process_graph": process_graph,
            "output": output
        }
    }
}

job_id ={
    "name": "job_id",
    "in": "path",
    "type": "string",
    "description": "Job identifier string",
    "required": True
}
