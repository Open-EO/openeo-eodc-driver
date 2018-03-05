from os import makedirs, listdir, path, walk
from shutil import copytree
from zipfile import ZipFile
from utils import read_parameters, read_input_mounts
from json import dump

OUT_VOLUME = "/job_results"
PARAMS = read_parameters()
INPUT_MOUNTS = read_input_mounts()

def copy_data():
    ''' Copies the data into the job result folder '''

    out_dir = "{0}/{1}".format(OUT_VOLUME, PARAMS["output"]["folder"])

    for mount in INPUT_MOUNTS:
        copytree("/" + mount, out_dir)

if __name__ == "__main__":
    print("Start result data copy process...")
    copy_data()
    print("Finish result data copy process.")
