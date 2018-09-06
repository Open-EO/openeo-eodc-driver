''' Utilities for Sentinel-2 data extraction '''

import json
from os import path, makedirs, listdir

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


def create_folder(base_folder, new_folder):
    '''Creates new_folder inside base_folder if it does not exist'''

    folder_path = "{0}/{1}".format(base_folder, new_folder)
    if not path.exists(folder_path):
        makedirs(folder_path)
    return folder_path


def write_output_to_json(data, operation_name, folder):
    '''Creates folder out_config in folder and writes data to json inside this new folder'''

    with open("{0}/files.json".format(folder), "w") as outfile:
        json.dump(data, outfile)


def get_paths_for_files_in_folder(folder_path):
    '''Returns a list of all file paths inside the given folder'''

    file_list = listdir(folder_path)

    files = []
    for file_path in file_list:
        if path.isfile(path.join(folder_path, file_path)):
            files.append("{0}/{1}".format(folder_path, file_path))

    return files

