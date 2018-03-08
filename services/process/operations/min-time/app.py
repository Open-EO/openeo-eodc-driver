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
         # Create dict to store data with date in
        data = None
        count = 0

        # Define output
        out_dataset = None
        out_path = "{0}/min-time_epsg-{1}-{2}.tif".format(OUT_FINAL, idx, PARAMS["data_srs"].split(":")[-1])  # TODO Add time range?

        with open("{0}/files.json".format(mount), 'r') as json_file:
            file_paths = load(json_file)["file_paths"]
            
            for file_path in file_paths:
                file_path = "{0}/{1}".format(mount, file_path)

                # Get data
                dataset = gdal.Open(file_path)
                band = dataset.GetRasterBand(1)
                file_data = band.ReadAsArray()

                if data is None:
                    data = numpy.zeros((len(file_paths), dataset.RasterYSize, dataset.RasterXSize))

                    # Save dummy out dataset to be filled with data
                    out_dataset = create_out_dataset(dataset, out_path)

                # Save data to dict
                data[count] = file_data

                count += 1

            min_time_data = numpy.minimum.reduce(data)

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

    write_output_to_json(data, "ndvi", OUT_VOLUME)


if __name__ == "__main__":
    print("Start processing 'min_time' ...")
    perform_min_time()
    write_output()
    print("Finished 'min_time' processing.")

