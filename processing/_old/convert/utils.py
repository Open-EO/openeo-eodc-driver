''' Utilities for Sentinel-2 data extraction '''

import json

CONFIG_FILE = "/job_config/config.json"

def read_parameters():
    ''' Return parameters from config file '''

    with open(CONFIG_FILE) as json_file:
        parameters = json.load(json_file)

    return parameters

def load_last_config(last_folder):
    with open("{0}/files.json".format(last_folder)) as json_file:
        config = json.load(json_file)

    return config