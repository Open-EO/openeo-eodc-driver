''' 

'''

from osgeo import gdal
import numpy
from json import load
from utils import read_parameters, read_input_mounts, create_folder, get_paths_for_files_in_folder, write_output_to_json

OUT_VOLUME = "/job_out"
OUT_FINAL = create_folder(OUT_VOLUME, "out_min-time")
PARAMS = read_parameters()
INPUT_MOUNTS = read_input_mounts()


def perform_min_time():
    ''' Performs min time '''

    print("-> Start calculating minimal NDVI...")

    # Iterate over each file and save the data
    for idx, mount in enumerate(INPUT_MOUNTS):

        # Create Out folders
        folder_stack_time_vrt = create_folder(OUT_VOLUME, "stack_time_vrt")
        folder_stack_time_tif = create_folder(OUT_VOLUME, "stack_time_tif")

        # Define output paths
        filename_part = "-time_epsg-{0}_mount-{1}".format(PARAMS["data_srs"].split(":")[-1], idx)
        path_time_stack_vrt = "{0}/stack{1}.vrt".format(folder_stack_time_vrt, filename_part)
        path_time_stack_tif = "{0}/stack{1}.tif".format(folder_stack_time_tif, filename_part)
        path_min_time = "{0}/min{1}.tif".format(OUT_FINAL, filename_part)

        with open("{0}/files.json".format(mount), 'r') as json_file:
            file_paths = load(json_file)["file_paths"]

            abs_file_paths = [mount + "/" + file_path for file_path in file_paths]

            # Combine all files into one (as different bands -> make sure they can be put on top of each other)
            gdal.BuildVRT(path_time_stack_vrt, abs_file_paths, separate=True)
            gdal.Translate(path_time_stack_tif, path_time_stack_vrt)

            dataset = gdal.Open(path_time_stack_tif)
            data = numpy.zeros((len(file_paths), dataset.RasterYSize, dataset.RasterXSize))
            out_dataset = create_out_dataset(dataset, path_min_time)  # Save dummy out dataset to be filled with data

            for band_num in range(0, len(file_paths)):

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

    write_output_to_json(data, OUT_VOLUME)


if __name__ == "__main__":
    print("Start processing 'min_time' ...")
    perform_min_time()
    write_output()
    print("Finished 'min_time' processing.")

