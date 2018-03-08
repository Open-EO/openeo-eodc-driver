''' Utilities for Sentinel-2 data extraction '''

import json
from os import path, makedirs, listdir

CONFIG_FILE = "/job_config/config.json"
IN_MOUNTS_FILE = "/job_config/input_mounts.json"


def read_parameters():
    ''' Return parameters from config file '''

    with open(CONFIG_FILE) as json_file:
        parameters = json.load(json_file)

    input_mounts = read_input_mounts()
    for mount in input_mounts:
        with open(mount + "/files.json") as json_file:
            for key, value in json.load(json_file).items():
                parameters[key] = value

    return parameters


def read_input_mounts():
    ''' Return parameters from config file '''

    with open(IN_MOUNTS_FILE) as json_file:
        input_mounts = json.load(json_file)

    return input_mounts


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
    return [folder_path + "/" + file for file in file_list]
