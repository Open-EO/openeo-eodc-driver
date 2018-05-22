from json import load
from osgeo import gdal
import numpy

from utils import read_parameters, create_folder, load_last_config,\
    write_output_to_json, get_paths_for_files_in_folder

PARAMS = read_parameters()
ARGS = PARAMS["args"]
OUT_VOLUME = "/job_data"

LAST_FOLDER = "{0}/{1}".format(OUT_VOLUME, PARAMS["last"])
LAST_CONFIG= load_last_config(LAST_FOLDER)
OUT_FOLDER = create_folder(OUT_VOLUME, PARAMS["template_id"])

def perform_ndvi():
    ''' Performs NDVI '''

    print("-> Start calculating NDVI...")
    for file_path in LAST_CONFIG["file_paths"]:
        filename = file_path.split("/")[-1]
        file_date = filename.split("_")[1]

        # Open input dataset
        file_path = "{0}/{1}".format(OUT_VOLUME, file_path)
        in_dataset = gdal.Open(file_path)

        # Calculate ndvi
        ndvi_data = calc_ndvi(in_dataset, LAST_CONFIG)

        # Save output dataset
        folder_ndvi = create_folder(OUT_FOLDER, "ndvi_first")
        out_file_path = "{0}/ndvi_{1}_epsg-{2}_first.tif".format(folder_ndvi, file_date, LAST_CONFIG["data_srs"].split(":")[-1])
        create_output_image(in_dataset, out_file_path, ndvi_data)

        # Warp out_files to create correct georeference
        out_file_path_warp = "{0}/ndvi_{1}_epsg-{2}.tif".format(OUT_FOLDER, file_date, LAST_CONFIG["data_srs"].split(":")[-1])
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

    data = {
        "product": LAST_CONFIG["product"],
        "operations": LAST_CONFIG["operations"] + ["ndvi"],
        "data_srs": LAST_CONFIG["data_srs"],
        "file_paths": get_paths_for_files_in_folder(OUT_FOLDER),
        "extent": LAST_CONFIG["extent"]
    }
    
    #TODO Anders
    cropped_paths = []
    for path in data["file_paths"]:
        cropped_paths.append(path.split("/", 2)[2])
    data["file_paths"] = cropped_paths

    write_output_to_json(data, "ndvi", OUT_FOLDER)

if __name__ == "__main__":
    print("Start processing 'NDVI' ...")
    perform_ndvi()
    write_output()
    print("Finished 'NDVI' processing.")

