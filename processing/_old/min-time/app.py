''' 

'''

from osgeo import gdal
import numpy
from json import load
from utils import read_parameters, load_last_config, create_folder, get_paths_for_files_in_folder, write_output_to_json

PARAMS = read_parameters()
ARGS = PARAMS["args"]
OUT_VOLUME = "/job_data"

LAST_FOLDER = "{0}/{1}".format(OUT_VOLUME, PARAMS["last"])
LAST_CONFIG= load_last_config(LAST_FOLDER)
OUT_FOLDER = create_folder(OUT_VOLUME, PARAMS["template_id"])


def perform_min_time():
    ''' Performs min time '''

    print("-> Start calculating minimal NDVI...")
    # Create Out folders
    folder_stack_time_vrt = create_folder(OUT_FOLDER, "stack_time_vrt")
    folder_stack_time_tif = create_folder(OUT_FOLDER, "stack_time_tif")

    # Define output paths
    filename_part = "-time_epsg-{0}".format(LAST_CONFIG["data_srs"].split(":")[-1])
    path_time_stack_vrt = "{0}/stack{1}.vrt".format(folder_stack_time_vrt, filename_part)
    path_time_stack_tif = "{0}/stack{1}.tif".format(folder_stack_time_tif, filename_part)
    path_min_time = "{0}/min{1}.tif".format(OUT_FOLDER, filename_part)

    abs_file_paths = [OUT_VOLUME + "/" + file_path for file_path in LAST_CONFIG["file_paths"]]

    # Combine all files into one (as different bands -> make sure they can be put on top of each other)
    gdal.BuildVRT(path_time_stack_vrt, abs_file_paths, separate=True)
    gdal.Translate(path_time_stack_tif, path_time_stack_vrt)

    dataset = gdal.Open(path_time_stack_tif)
    data = numpy.zeros((len(LAST_CONFIG["file_paths"]), dataset.RasterYSize, dataset.RasterXSize))
    out_dataset = create_out_dataset(dataset, path_min_time)  # Save dummy out dataset to be filled with data

    for band_num in range(0, len(LAST_CONFIG["file_paths"])):

        band = dataset.GetRasterBand(band_num + 1)
        file_data = band.ReadAsArray()

        # Save data to dict
        data[band_num] = file_data

    min_time_data = numpy.fmin.reduce(data)

    # Write data to dataset
    fill_dataset(out_dataset, min_time_data)

    print("-> Finished calculating minimal NDVI")


def create_out_dataset(in_dataset, out_path):
    '''Create output dataset'''

    driver = gdal.GetDriverByName("GTiff")

    # Create output file from input (only one band)
    out_dataset = driver.Create(out_path, in_dataset.RasterXSize, in_dataset.RasterYSize, 1, gdal.GDT_Float32)

    # Add spatial information from input dataset
    out_dataset.SetGeoTransform(in_dataset.GetGeoTransform())
    out_dataset.SetProjection(in_dataset.GetProjection())

    # Write to disk
    out_dataset.FlushCache()

    return out_dataset


def fill_dataset(dataset, data):
    '''Fill empty dataset with data'''

    # Add data
    band = dataset.GetRasterBand(1)
    band.WriteArray(data)
    band.SetNoDataValue(2)

    # Write to disk
    dataset.FlushCache()


def write_output():
    '''Writes output's metadata to file'''

    data = {"product": LAST_CONFIG["product"],
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

    write_output_to_json(data, OUT_FOLDER)


if __name__ == "__main__":
    print("Start processing 'min_time' ...")
    perform_min_time()
    write_output()
    print("Finished 'min_time' processing.")

