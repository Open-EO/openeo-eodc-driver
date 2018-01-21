filterbbox = {
    "process_id": "filter_bbox",
    "description": "Drops observations from a collection that are located outside of a given bounding box.",
    "type": "filter",
    "args": {
        "collections": {
            "description": "array of input collections with one element",
            "required": True
        },
        "left": {
            "description": "left boundary (longitude / easting)",
            "bind": "FBBX_LEFT",
            "required": True
        },
        "right":{
            "description": "right boundary (longitude / easting)",
            "bind": "FBBX_RIGHT",
            "required": True
        },
        "top": {
            "description": "top boundary (latitude / northing)",
            "bind": "FBBX_TOP",
            "required": True
        },
        "bottom": {
            "description": "bottom boundary (latitude / northing)",
            "bind": "FBBX_BOTTOM",
            "required": True
        },
        "srs": {
            "description": "spatial reference system of boundaries as proj4 or EPSG:12345 like string",
            "bind": "FBBX_SRS",
            "required": True
        }
    }
}

filterdaterange = {
    "process_id": "filter_daterange",
    "description": "Drops observations from a collection that have been captured before a start or after a given end date.",
    "type": "filter",
    "args": {
        "collections": {
            "description": "array of input collections with one element",
            "required": True
        },
        "from" : {
            "description" : "start date",
            "required": True
        },
        "to" : {
            "description" : "end date",
            "required": True
        }
    }
}

ndvi = {
    "process_id": "NDVI",
    "description": "Finds the minimum value of time series for all bands of the input dataset.",
    "git_uri": "git@git.eodc.eu:eodc-processes/ndvi.git",
    "git_ref": "master",
    "type": "operation",
    "args": {
        "collections": {
            "description": "array of input collections with one element",
            "required": True
        },
        "red" : {
            "description" : "reference to the red band",
            "required": True
        },
        "nir" : {
            "description" : "reference to the nir band",
            "required": True
        }
    }
}

mintime = {
    "process_id": "min_time",
    "description": "Finds the minimum value of time series for all bands of the input dataset.",
    "git_uri": "git@git.eodc.eu:eodc-processes/min-time.git",
    "git_ref": "master",
    "type": "operation",
    "args": {
        "collections": {
            "description": "array of input collections with one element",
            "required": True
        }
    }
}

extractfromstorage = {
    "process_id": "extract-from-storage",
    "description": "Extracts data from EODC storage to a mounted volume.",
    "git_uri": "git@git.eodc.eu:eodc-processes/extract-from-storage.git",
    "git_ref": "master",
    "type": "operation",
    "args": {
        "urls": {
            "description": "URLS to query EODC data service for file paths",
            "required": True
        }
    }
}