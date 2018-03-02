''' 

'''

from os import makedirs, listdir
from zipfile import ZipFile
from utils import read_parameters
from time import sleep

OUT_VOLUME = "/job_out"
PARAMS = read_parameters()

def perform_ndvi():
    ''' Performs min time '''

    print("Doing something...")
    sleep(2)
    print("Finished doing something.")


if __name__ == "__main__":
    print("Start processing 'min_time' ...")
    perform_ndvi()
    print("Finished 'min_time' processing.")