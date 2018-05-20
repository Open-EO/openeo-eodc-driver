''' 
Sentinel-2 NDVI calculation

Parameters
----------
product: string
    basic dataset product
    > product: "Sentinel-2"

operations: array of strings
    applied processing steps / operations
    > operations: ["filter-s2"]

band_order: dict
    band name (str): band number in input dataset (int)
    For band name Sentinel-2 notation (e.g.: B01) is assumed
    > band_order: {"B03": 1}

data_srs: string
    Spatial reference system of data as EPSG:4326 atring
    combination of EPSG:4326 like string
    > data_srs:"EPSG:4326"

file_paths: array of strings
    list of file paths to input files
    filename is like: filter-s2_DATE_epsg-EPSGNUMBER.tif (e.g.: filter-s2_2017-12-07_epsg-4326.tif)

extent: dict
    bbox: dict
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

# OUTPUTS
    Output contains ndvi data per day

# Volumes
- /job_config -> Configuration mount
- /job_out -> output mount
- /job_in -> input mount ??

'''

from json import load
from osgeo import gdal
import numpy

from utils import read_parameters, read_input_mounts, create_folder, \
    write_output_to_json, get_paths_for_files_in_folder
OUT_VOLUME = "/job_out"
OUT_FINAL = create_folder(OUT_VOLUME, "out_ndvi")
PARAMS = read_parameters()
INPUT_MOUNTS = read_input_mounts()


def perform_ndvi():
    ''' Performs NDVI '''

    print("-> Start calculating NDVI...")

    # Iterate over each file
    for mount in INPUT_MOUNTS:
        with open("{0}/files.json".format(mount), 'r') as json_file:
            file_param = load(json_file)
            file_paths = file_param["file_paths"]

            for file_path in file_paths:
                filename = file_path.split("/")[-1]
                file_date = filename.split("_")[1]

                # Open input dataset
                file_path = "{0}/{1}".format(mount, file_path)
                in_dataset = gdal.Open(file_path)

                # Calculate ndvi
                ndvi_data = calc_ndvi(in_dataset, file_param)

                # Save output dataset
                folder_ndvi = create_folder(OUT_VOLUME, "ndvi_first")
                out_file_path = "{0}/ndvi_{1}_epsg-{2}_first.tif".format(folder_ndvi, file_date, PARAMS["data_srs"].split(":")[-1])
                create_output_image(in_dataset, out_file_path, ndvi_data)

                # Warp out_files to create correct georeference
                out_file_path_warp = "{0}/ndvi_{1}_epsg-{2}.tif".format(OUT_FINAL, file_date, PARAMS["data_srs"].split(":")[-1])
                gdal.Warp(out_file_path_warp, out_file_path)

                print(" - NDVI calculated for {0}".format(filename))

    print("-> Finished calculating NDVI.")


def create_output_image(in_dataset, out_file_path, out_data):
    '''Create and save output dataset'''

    driver = gdal.GetDriverByName("GTiff")

    # Create output file from input (only one band)
    out_dataset = driver.Create(out_file_path, in_dataset.RasterXSize, in_dataset.RasterYSize, 1, gdal.GDT_Float32)

    # Add spatial information from input dataset
    out_dataset.SetGeoTransform(in_dataset.GetGeoTransform())
    out_dataset.SetProjection(in_dataset.GetProjection())

    # Add data
    band = out_dataset.GetRasterBand(1)
    band.WriteArray(out_data)
    band.SetNoDataValue(2)

    # Write to disk
    out_dataset.FlushCache()


def get_band_data(dataset, band_number):
    '''Returns band data for given dataset and band_name, the noDataValue is set to NaN'''

    # TODO check if band is in dataset

    band = dataset.GetRasterBand(band_number)
    data = band.ReadAsArray()

    # Set noDataValue to NaN
    data = data.astype(float)
    data = set_no_data(data, band.GetNoDataValue(), numpy.nan)

    return data


def set_no_data(data, cur, should):
    '''Set no data value'''

    data[data == cur] = should
    return data


def calc_ndvi(dataset, file_param):
    '''Returns ndvi for given red and nir band (no data is set to 2, ndvi in range [-1, 1])'''

    # Get band data
    red = get_band_data(dataset, file_param["band_order"]["B04"])
    nir = get_band_data(dataset, file_param["band_order"]["B08"])

    # Calculate NDVI
    ndvi = (nir - red) / (nir + red)
    ndvi = set_no_data(ndvi, numpy.nan, 2)
    return ndvi


def write_output():
    '''Writes output's metadata to file'''

    data = {"product": PARAMS["product"],
            "operations": PARAMS["operations"] + ["ndvi"],
            "data_srs": PARAMS["data_srs"],
            "file_paths": get_paths_for_files_in_folder(OUT_FINAL),
            "extent": PARAMS["extent"]
            }
    
    #TODO Anders
    cropped_paths = []
    for path in data["file_paths"]:
        cropped_paths.append(path.split("/", 2)[2])
    data["file_paths"] = cropped_paths

    write_output_to_json(data, "ndvi", OUT_VOLUME)

if __name__ == "__main__":
    print("Start processing 'NDVI' ...")
    perform_ndvi()
    write_output()
    print("Finished 'NDVI' processing.")

