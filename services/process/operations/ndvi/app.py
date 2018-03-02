''' 

'''

from os import makedirs, listdir
from zipfile import ZipFile
from utils import read_parameters
from time import sleep

OUT_VOLUME = "/job_out"
PARAMS = read_parameters()

def perform_ndvi():
    ''' Performs NDVI '''

    print("Doing something...")
    sleep(2)
    print("Finished doing something.")


if __name__ == "__main__":
    print("Start processing 'NDVI' ...")
    perform_ndvi()
    print("Finished 'NDVI' processing.")