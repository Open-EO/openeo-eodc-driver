from os import makedirs, listdir, path, walk
from shutil import copyfile
from zipfile import ZipFile
from utils import read_parameters, load_last_config
from json import dump, load

IN_VOLUME  = "/job_data" 
OUT_VOLUME = "/job_results"
PARAMS = read_parameters()
ARGS = PARAMS["args"]

LAST_FOLDER = "{0}/{1}".format(IN_VOLUME, PARAMS["last"])
LAST_CONFIG= load_last_config(LAST_FOLDER)

def copy_data():
    ''' Copies the data into the job result folder '''

    out_dir = "{0}/{1}".format(OUT_VOLUME, ARGS["job_id"])

    if not path.exists(out_dir):
        makedirs(out_dir)

    for file_path in LAST_CONFIG["file_paths"]:
        file_path = "{0}/{1}".format(IN_VOLUME, file_path)
        file_name = file_path.split("/")[-1]
        copyfile(file_path, "{0}/{1}".format(out_dir, file_name))
        print(" -> Copied file: " + file_path)

if __name__ == "__main__":
    print("Start result data copy process...")
    copy_data()
    print("Finish result data copy process.")
