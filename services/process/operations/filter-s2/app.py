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

from os import listdir
from shutil import copyfile, rmtree
from zipfile import ZipFile

from osgeo import gdal, osr

OUT_VOLUME = "/job_out"
from utils import read_parameters, build_new_img_name_from_old, build_new_granule_name_from_old, create_folder, \
    write_output_to_json, get_paths_for_files_in_folder

OUT_FINAL = create_folder(OUT_VOLUME, "out_filter-s2")
PARAMS = read_parameters()
OUT_EPSG = "4326"
TEMP_FOLDERS = {}  # tmp folder: tmp folder path -> deleted in the end


def unzip_data():
    ''' Unzips the files from EODC storage to out volume '''

    print("-> Start data unzipping...")

    TEMP_FOLDERS["unzipped"] = create_folder(OUT_VOLUME, "01_unzipped")
    for day, file_paths_per_day in PARAMS["file_paths"].items():

        # create a Out folder for each day (eg: /job_out/unzipped/2018-02-06/)
        unzip_path = create_folder(TEMP_FOLDERS["unzipped"], day)

        # extract all files of current day
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
    TEMP_FOLDERS["extracted"] = create_folder(OUT_VOLUME, "02_extracted")

    for day in PARAMS["file_paths"].keys():

        # Create Out folder for each day inside "extracted" folder
        folder_day = create_folder(TEMP_FOLDERS["extracted"], day)

        # Iterate over each day folder in unzipped (observation: path to archive on eodc storage)
        for observation in listdir("{0}/{1}".format(TEMP_FOLDERS["unzipped"], day)):
            for granule in listdir("{0}/{1}/{2}/GRANULE".format(TEMP_FOLDERS["unzipped"], day, observation)):

                dst_granule = granule
                # Check for old S2 naming convention
                if granule.startswith("S"):
                    dst_granule = build_new_granule_name_from_old(granule)

                # Create a folder for each granule
                folder_granule = create_folder(folder_day, dst_granule)

                img_path = "{0}/{1}/{2}/GRANULE/{3}/IMG_DATA".format(TEMP_FOLDERS["unzipped"], day, observation, granule)
                for img_name in listdir(img_path):
                    file_band = img_name.split("_")[-1].split(".")[0]

                    if file_band in PARAMS["bands"] or not PARAMS["bands"]:

                        dst_img_name = img_name
                        # Check for old S2 naming convention
                        if img_name.startswith("S"):
                            dst_img_name = build_new_img_name_from_old(img_name)

                        src = "{0}/{1}".format(img_path, img_name)
                        dst = "{0}/{1}".format(folder_granule, dst_img_name)
                        copyfile(src, dst)

                        print(" - Extracted {0}".format(dst_img_name))

    print("-> Finished data extraction.")


def combine_bands():
    '''Combines all specified bands per file'''

    print("-> Start combining bands...")

    # Create Out folder
    TEMP_FOLDERS["combined_bands"] = create_folder(OUT_VOLUME, "03_combined_bands")

    # Iterate over each day
    for day in PARAMS["file_paths"].keys():

        # Create one folder per day
        folder_day = create_folder(TEMP_FOLDERS["combined_bands"], day)

        # Iterate over each granule
        for granule in listdir("{0}/{1}".format(TEMP_FOLDERS["extracted"], day)):

            # Get list of input files
            band_path_list = get_paths_for_files_in_folder("{0}/{1}/{2}/".format(TEMP_FOLDERS["extracted"], day, granule))
            band_path_list.sort()  # make sure bands are always in same order

            # Build out_path (filename without file extension and band number)
            out_filename = "{0}.vrt".format(band_path_list[0].split("/")[-1].split(".")[0][:-4])
            out_path = "{0}/{1}".format(folder_day, out_filename)

            # Combine all dataset bands in one vrt-file
            gdal.BuildVRT(out_path, band_path_list, separate=True, srcNodata=0)
            print(" - Combined bands for {0}".format(out_filename))

    print("-> Finished combining bands.")


def combine_same_utm():
    '''Combines all files within one UTM zone in on vrt-file (per day)'''

    print("-> Start combining same UTM zone...")

    # Create Out folder
    TEMP_FOLDERS["utm"] = create_folder(OUT_VOLUME, "04_combined_utm")

    # iterate over each day
    for day in PARAMS["file_paths"].keys():

        # Create one folder per day
        folder_day = create_folder(TEMP_FOLDERS["utm"], day)

        # Sort files after their UTM zone
        zones = {}
        for file in listdir("{0}/{1}".format(TEMP_FOLDERS["combined_bands"], day)):
            file_path = "{0}/{1}/{2}".format(TEMP_FOLDERS["combined_bands"], day, file)

            cur_zone = file[1:3]
            if cur_zone not in zones:
                zones[cur_zone] = [file_path]
            else:
                zones[cur_zone].append(file_path)

        # Iterate over UTM zones in dict
        for zone in zones.keys():
            # Build out_path
            out_filename = "T{0}_{1}.vrt".format(zone, day)
            out_path = "{0}/{1}".format(folder_day, out_filename)

            # Merge all vrt-files inside one UTM zone
            gdal.BuildVRT(out_path, zones[zone])
            print(" - Combined UTM for {0}".format(out_filename))

    print("-> Finished combining same UTM zone.")


def reproject():
    '''Reprojects all UTM zones into specified reference system'''

    print("-> Start reprojection...")

    # Create Out folder with subfolders for each day
    TEMP_FOLDERS["reproject"] = create_folder(OUT_VOLUME, "05_reproject")

    for day in PARAMS["file_paths"].keys():

        # Create one folder per day
        folder_day = create_folder(TEMP_FOLDERS["reproject"], day)

        for utm_file in listdir("{0}/{1}".format(TEMP_FOLDERS["utm"], day)):

            # Get input path
            in_path = "{0}/{1}/{2}".format(TEMP_FOLDERS["utm"], day, utm_file)

            # Build output path
            out_filename = "{0}_epsg{1}.vrt".format(utm_file.split(".")[0], OUT_EPSG)
            out_path = "{0}/{1}".format(folder_day, out_filename)

            # Reproject each utm file to set epsg
            gdal.Warp(out_path, in_path, dstSRS="EPSG:{0}".format(OUT_EPSG), format="vrt")
            print(" - Reprojected {0}".format(out_filename))

    print("-> Finished reprojection.")


def merge_reprojected():
    '''Merges all reprojected files and applies bbox'''

    print("-> Start merging...")

    # Create Out folder
    TEMP_FOLDERS["merged"] = create_folder(OUT_VOLUME, "06_merged")

    PARAMS["bbox_out_epsg"] = None

    for day in PARAMS["file_paths"].keys():

        # Get input path
        file_path_list = get_paths_for_files_in_folder("{0}/{1}/".format(TEMP_FOLDERS["reproject"], day))

        # Build output path
        out_filename = "filter-s2_{0}_epsg-{1}.vrt".format(day, OUT_EPSG)
        out_path = "{0}/{1}".format(TEMP_FOLDERS["merged"], out_filename)

        if PARAMS["bbox_out_epsg"] is None:
            PARAMS["bbox_out_epsg"] = get_bbox()

        # Merge all files into one vrt-file
        gdal.BuildVRT(out_path, file_path_list, outputBounds=PARAMS["bbox_out_epsg"])
        print(" - Merged {0}".format(out_filename))

    print("-> Finished merging.")


def transform_to_geotiff():
    '''Translates merged vrt-file to GeoTiff'''

    print("-> Start translation to GeoTiff...")

    for file in listdir(TEMP_FOLDERS["merged"]):

        # Get input path
        in_path = "{0}/{1}".format(TEMP_FOLDERS["merged"], file)

        # Build output path
        out_filename = "{0}.tif".format(file.split(".")[0])
        out_path = "{0}/{1}".format(OUT_FINAL, out_filename)

        # Translate vrt-file to GeoTiff
        gdal.Translate(out_path, in_path, outputBounds=PARAMS["bbox_out_epsg"])  # TODO show progress somehow (slow!)
        print(" - Translated {0}".format(out_filename))

    print("-> Finished translation to GeoTiff.")


def get_bbox():
    '''Returns bbox in specified reference system
    :return bbox:[left, bottom, right, top] - array of numbers'''

    bbox_epsg = PARAMS["srs"].split(":")[1]

    # Transform bbox coordinates to reference system of data
    if OUT_EPSG != bbox_epsg:

        # Get spatial reference system of the bbox and the specified one
        bbox_srs = osr.SpatialReference()
        bbox_srs.ImportFromEPSG(int(bbox_epsg))
        data_srs = osr.SpatialReference()
        data_srs.ImportFromEPSG(int(OUT_EPSG))

        # Get Transformation
        transform = osr.CoordinateTransformation(bbox_srs, data_srs)

        # Transform all corner points
        left_bottom = transform.TransformPoint(PARAMS["left"], PARAMS["bottom"])
        left_top = transform.TransformPoint(PARAMS["left"], PARAMS["top"])
        right_top = transform.TransformPoint(PARAMS["right"], PARAMS["top"])
        right_bottom = transform.TransformPoint(PARAMS["right"], PARAMS["bottom"])

        # Find max/min for each corner
        left = min(left_bottom[0], left_top[0])
        right = max(right_bottom[0], right_top[0])
        bottom = min(left_bottom[1], right_bottom[1])
        top = max(left_top[1], right_top[1])

        if bottom > top:
            tmp = bottom
            bottom = top
            top = tmp

        if left > right:
            tmp = right
            right = left
            left = tmp
        
        return [left, bottom, right, top]

        # return [left, top, right, bottom]

    else:
        return [PARAMS["left"], PARAMS["bottom"], PARAMS["right"], PARAMS["top"]]


def write_output():
    '''Writes output's metadata to file'''

    # TODO Bands in Metadaten -> Übergeben als Parameter / Kein empty array
    bands = PARAMS["bands"]
    if not bands:
        bands = ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B09", "B10", "B11", "B12", "TCI"]

    # save band_order
    bands.sort()
    order = range(1, len(bands)+1)
    band_order = dict(zip(bands, order))

    data = {"product": "Sentinel-2",
            "operations": ["filter-s2"],
            "band_order": band_order,
            "data_srs": "EPSG:{0}".format(OUT_EPSG),
            "file_paths": get_paths_for_files_in_folder(OUT_FINAL),
            "extent": {
                "bbox": {
                    "top": PARAMS["top"],
                    "bottom": PARAMS["bottom"],
                    "left": PARAMS["left"],
                    "right": PARAMS["right"]},
                "srs": PARAMS["srs"]},
            }

    #TODO Anders
    cropped_paths = []
    for path in data["file_paths"]:
        cropped_paths.append(path.split("/", 2)[2])
    data["file_paths"] = cropped_paths
    
    write_output_to_json(data, "filter-s2", OUT_VOLUME)


def clean_up():
    '''Deletes all unnecessary folders'''

    print("-> Start clean up...")

    for folder_path in TEMP_FOLDERS.keys():
        rmtree(TEMP_FOLDERS[folder_path])

    print("-> Finished clean up.")


    print(listdir(OUT_VOLUME))

if __name__ == "__main__":
    print("Start Sentinel 2 data extraction process...")

    unzip_data()
    extract_sentinel_2_data()
    combine_bands()
    combine_same_utm()
    reproject()
    merge_reprojected()
    transform_to_geotiff()
    write_output()
    clean_up()

    print("Finished Sentinel 2 data extraction process.")
