''' Utilities for Sentinel-2 data extraction '''

import json

CONFIG_FILE = "/job_config/config.json"

def read_parameters():
    ''' Return parameters from config file '''

    with open(CONFIG_FILE) as json_file:
        parameters = json.load(json_file)

    return parameters
