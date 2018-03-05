''' 
Sentinel-2 Data extraction

Parameters
----------
file_paths: dict
    File-Paths per day (as array) to Sentinel-2 data on EODC storage
    > file_paths: {
        "2017-02-01": ["/eodc/products/...", "/eodc/products/..."],
        ...
    }
left: number
    Left boundary (longitude / easting) in EPSG:32632
    > left:652000
right: int
    Right boundary (longitude / easting)
    > right:672000
top: int
    Top boundary (latitude / northing)
    > top:5161000
bottom: int
    Bottom boundary (latitude / northing)
    > bottom:5181000
srs: string
    Spatial reference system of boundaries as proj4 or EPSG:12345 like string
    > srs: "EPSG:32632"
bands: array
    Array of numbers containing band ids.
    bands: [1,2,5]

# OUPUTS
    Ouput volume contains the extracted, cropped and stitched band Sentinel-2 data per day

# Volumes
- /eodc -> EODC storage
- /job_config -> Configuration mount
- /job_out -> Output mount
'''

from os import makedirs, listdir, path
from shutil import copyfile, rmtree
from zipfile import ZipFile
from utils import read_parameters
from json import dump

OUT_VOLUME = "/job_out"
PARAMS = read_parameters()

def unzip_data():
    ''' Unzips the files from EODC storage to out volume '''

    print("-> Start data unzipping...")

    for day, file_paths_per_day in PARAMS["file_paths"].items():
        unzip_path = "{0}/unzipped/{1}".format(OUT_VOLUME, day)
        if not path.exists(unzip_path):
            makedirs(unzip_path)

        for zip_path in file_paths_per_day:
            zip_ref = ZipFile(zip_path, 'r')
            zip_ref.extractall(unzip_path)
            zip_ref.close()

            print(" - Unzipped {0}".format(zip_path))

    print("-> Finished data unzipping.")

def extract_sentinel_2_data():
    ''' Extracts data that is specified by PARAMS '''
    
    print("-> Start data extraction...")

    # Create Out folder
    folder_extracted = "{0}/extracted".format(OUT_VOLUME)
    if not path.exists(folder_extracted):
        makedirs(folder_extracted)

    folder_unzipped = "{0}/unzipped/".format(OUT_VOLUME)
    processed = []
    for day_folder in listdir(folder_unzipped):
        out_day = "{0}/{1}".format(folder_extracted, day_folder)
        if not path.exists(out_day):
            makedirs(out_day)
        for observation in listdir("{0}/unzipped/{1}".format(OUT_VOLUME, day_folder)):
            for granule in listdir("{0}/unzipped/{1}/{2}/GRANULE".format(OUT_VOLUME, day_folder, observation)):
                img_path = "{0}/unzipped/{1}/{2}/GRANULE/{3}/IMG_DATA".format(OUT_VOLUME, day_folder, observation, granule)
                for img_name in listdir(img_path):
                    file_band = img_name.split("_")[-1].split(".")[0]

                    if file_band in PARAMS["bands"] or not PARAMS["bands"]:
                        src = "{0}/{1}".format(img_path, img_name)
                        dst = "{0}/{1}".format(out_day, img_name)
                        copyfile(src, dst)

                        file_path = dst.split("/", 2)[2]

                        processed.append(
                            {
                                "file_name": img_name,
                                "file_path": file_path,
                                "product": "Sentinel-2",
                                "bands": [file_band],
                                "extend": {
                                    "bbox": {
                                        "top": PARAMS["top"], 
                                        "right": PARAMS["right"], 
                                        "bottom": PARAMS["bottom"], 
                                        "left": PARAMS["left"]
                                    },
                                    "srs": PARAMS["srs"]
                                },
                                "operations": ["filter-s2"]
                            }
                        )

                        print(" - Extracted {0}".format(img_name))
    
    rmtree(folder_unzipped)

    with open("{0}/files.json".format(OUT_VOLUME), 'w') as outfile:
        dump(processed, outfile)

    print("-> Finished data extraction.")

    print(listdir(OUT_VOLUME))

if __name__ == "__main__":
    print("Start Sentinel 2 data extraction process...")

    unzip_data()
    extract_sentinel_2_data()
    # TODO: filter_bands()
    # TODO: stitch_data()
    # TODO: clean_up()



    print("Finished Sentinel 2 data extraction process.")

    ## Parameters
    # file_paths = PARAMS["file_paths"]
    # left = PARAMS["left"]
    # right = PARAMS["right"]
    # top = PARAMS["top"]
    # bottom = PARAMS["bottom"]
    # srs = PARAMS["srs"]
    # bands = PARAMS["bands"]

    