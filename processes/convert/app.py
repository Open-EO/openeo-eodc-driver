from os import makedirs, listdir, path, walk
from shutil import copyfile
from zipfile import ZipFile
from utils import read_parameters, read_input_mounts
from json import dump, load

OUT_VOLUME = "/job_results"
PARAMS = read_parameters()
INPUT_MOUNTS = read_input_mounts()

def copy_data():
    ''' Copies the data into the job result folder '''

    out_dir = "{0}/{1}".format(OUT_VOLUME, PARAMS["output"]["folder"])

    if not path.exists(out_dir):
        makedirs(out_dir)

    for mount in INPUT_MOUNTS:
        with open("{0}/files.json".format(mount), 'r') as json_file:
            file_paths = load(json_file)["file_paths"]

        for file_path in file_paths:
            file_path = "{0}/{1}".format(mount, file_path)
            file_name = file_path.split("/")[-1]
            copyfile(file_path, "{0}/{1}".format(out_dir, file_name))
            print(" -> Copied file: " + file_path)

if __name__ == "__main__":
    print("Start result data copy process...")
    copy_data()
    print("Finish result data copy process.")
