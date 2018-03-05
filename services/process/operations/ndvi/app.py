''' 

'''

from os import makedirs, listdir
from zipfile import ZipFile
from utils import read_parameters, read_input_mounts
from time import sleep
from shutil import copyfile, rmtree
from json import load, dump

OUT_VOLUME = "/job_out"
PARAMS = read_parameters()
INPUT_MOUNTS = read_input_mounts()

def perform_ndvi():
    ''' Performs NDVI '''

    print("Doing something...")

    processed = []
    for mount in INPUT_MOUNTS:
        print(listdir("/" + mount))
        with open("/{0}/files.json".format(mount), 'r') as json_file:
            files = load(json_file)

        for file_data in files:
            copyfile(
                "{0}/{1}".format(mount, file_data["file_path"]), 
                "{0}/{1}".format(OUT_VOLUME, file_data["file_name"]))

            print("Copyed file: " + file_data["file_name"])

            file_data["file_path"] = file_data["file_name"]
            file_data["operations"].append("min_time")
            processed.append(file_data)

    with open("/{0}/files.json".format(OUT_VOLUME), 'w') as outfile:
        dump(processed, outfile)
    
    print("Finished doing something.")
    print(listdir(OUT_VOLUME))


if __name__ == "__main__":
    print("Start processing 'NDVI' ...")
    perform_ndvi()
    print("Finished 'NDVI' processing.")