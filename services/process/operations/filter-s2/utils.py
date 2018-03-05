''' Utilities for Sentinel-2 data extraction '''

import json
from os import path, makedirs, listdir

CONFIG_FILE = "/job_config/config.json"

def read_parameters():
    ''' Return parameters from config file '''

    with open(CONFIG_FILE) as json_file:
        parameters = json.load(json_file)

    return parameters


def create_folder(base_folder, new_folder):
    folder_path = "{0}/{1}".format(base_folder, new_folder)
    if not path.exists(folder_path):
        makedirs(folder_path)
    return folder_path


def get_paths_for_files_in_folder(folder_path):
    file_list = listdir(folder_path)
    return [folder_path + file for file in file_list]


def build_new_granule_name_from_old(granule_name):
    '''Builds the corresponding new granule name from an old S2 name'''

    granule_name_split = granule_name.split("_")

    parts = {"proc_level": granule_name_split[3],
             "tile_number": granule_name_split[-2],
             "absolut_orbit": granule_name_split[-3],
             "date": granule_name_split[-4]}

    return "{0}_{1}_{2}_{3}".format(parts["proc_level"], parts["tile_number"], parts["absolut_orbit"], parts["date"])


def build_new_img_name_from_old(img_name):
    '''Builds the corresponding new image name form an old S2 name'''

    img_name_split = img_name.split(".")[0].split("_")

    parts = {"band": img_name_split[-1],
             "tile_number": img_name_split[-2],
             "date": img_name_split[-4]}

    return "{0}_{1}_{2}.jp2".format(parts["tile_number"], parts["date"], parts["band"])
