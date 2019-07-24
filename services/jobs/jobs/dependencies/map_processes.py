"""
A module dostring.
"""

import os
from owslib.csw import CatalogueServiceWeb
from owslib.fes import PropertyIsLike, BBox, PropertyIsLessThan, PropertyIsGreaterThan


def map_process(process, process_name, process_id, root_folder, options=None):
    """
    Entry point.
    """


    if not options:
        options = []

    filepaths = None

    # Add/set output folder
    map_set_set_output_folder(root_folder, process_id, options)

    if process['process_id'] in ('get_data', 'get_collection', 'load_collection'):
        dict_items, filepaths = map_get_collection(process)
        input_type = "single_file"
    elif process['process_id'].lower() == 'ndvi':
        dict_items = map_process_ndvi(process)
        input_type = "multiple_files"
    elif process['process_id'].lower() in ('min', 'max', 'mean'):
        if 'min' in process['process_id'].lower():
            keyword = 'min'
        elif 'max' in process['process_id'].lower():
            keyword = 'max'
        elif 'mean' in process['process_id'].lower():
            keyword = 'mean'
        dict_items = map_process_temporal_statistics(process, keyword)
        input_type = "multiple_files"
    elif process['process_id'].lower() == 'reduce':
        process = {'arguments': {'format': 'vrt'}}
        dict_items = map_save_result(process)
        input_type = "single_file"
        # dict_items, input_type, _ = map_process(process=reducer_graph, process_name=reducer_name, process_id=reducer_id)
        # _ = dict_items.pop(0)
    elif process['process_id'].lower() == 'save_result':
        dict_items = map_save_result(process)
        input_type = "single_file"

    if not isinstance(dict_items, list):
        dict_items = [dict_items]
    for dict_item in dict_items:
        options.append(dict_item)

    return options, input_type, filepaths


def map_save_result(process):
    """

    """

    dict_item_list = [
                {'name': 'add_band', 'bands': 1},
                {'name': 'save_raster', 'bands': 'B1-F1', 'format_type':  process['arguments']['format']}
                ]

    return dict_item_list

def map_set_set_output_folder(root_folder, folder_name, options=[]):
    """
    Appends folder to options.
    """

    # Set output_folder for this operation
    dict_item = {'name': 'set_output_folder',\
                 'folder_name': root_folder + os.path.sep + folder_name + os.path.sep,\
                 'absolute_path': '1;int'}

    # Set output_folder for this operation
    # if process['imagery_id']:
    #     dict_item = {'name': 'set_output_folder',\
    #                  'folder_name': JOB_DATA + os.path.sep + process['imagery_id'] + os.path.sep,\
    #                  'absolute_path': '1;int'}
    # else:
    #     dict_item = {'name': 'set_output_folder',\
    #                  'folder_name': JOB_DATA + os.path.sep + 'final' + os.path.sep,\
    #                  'absolute_path': '1;int'}


    return options.append(dict_item)


def map_filter_bands(process):
    """

    """

    dict_item_list = []

    if 'bands' in process['arguments'].keys():
        load_bands = process['arguments']['bands']
    elif 'names' in process['arguments'].keys():
        load_bands = process['arguments']['names']
    # elif 'wavelenghts' in process['args'].keys():
    #     # add this option
    else:
        load_bands = 'all'

    dict_item = {'name': 'add_band', 'bands': load_bands}
    dict_item_list.append(dict_item)

    return dict_item_list


def map_filter_bbox(process):
    """

    """

    # TODO support fields 'base' and 'height'

    dict_item_list = []

    if 'spatial_extent' in process['arguments'].keys():
        bbox = (process['arguments']['spatial_extent']['west'], process['arguments']['spatial_extent']['south'],\
                process['arguments']['spatial_extent']['east'], process['arguments']['spatial_extent']['north'])
        if 'crs' in process['arguments']['spatial_extent'].keys():
            crs_value = process['arguments']['spatial_extent']['crs']
        else:
            crs_value = 'EPSG:4326'
        dict_item = {'name': 'crop', 'bbox': bbox, 'crs': crs_value}
        dict_item_list.append(dict_item)

    return dict_item_list

def map_get_collection(process):
    """
    Retrieves a file list and maps bbox and band filters to eoDataReaders.
    """

    # Get list of filepaths fro csw server
    filepaths = csw_query(collection=process['arguments']["id"],
                          spatial_extent=(
                              process['arguments']['spatial_extent']['south'],
                              process['arguments']['spatial_extent']['west'],
                              process['arguments']['spatial_extent']['north'],
                              process['arguments']['spatial_extent']['east']
                              ),
                          temporal_extent=process['arguments']["temporal_extent"]
                         )

    dict_item_list = []

    # Map band filter
    if 'bands' in process['arguments'].keys():
        dict_item = map_filter_bands(process)[0]
    else:
        dict_item = map_filter_bands({'arguments': {'bands': 'all'}})[0]
    dict_item_list.append(dict_item)

    # Map bbox filter
    if 'spatial_extent' in process['arguments'].keys():
        dict_item = map_filter_bbox(process)[0]
        dict_item_list.append(dict_item)

    return dict_item_list, filepaths


def map_process_ndvi(process):
    """
    Map openEO NDVI to eoDataReader dict input.
    """

    #input_bands = [int(process['args']['red']), int(process['args']['nir'])]

    dict_item = [
        #{'name': 'add_band', 'bands': input_bands, 'file_num': 'all'},
        {'name': 'add_band', 'bands': 1, 'file_num': 'all'},
        {'name': 'eo_function', 'group_bands': True, 'f_input': {'f_name' : 'ndvi'}}
        ]

    return dict_item


def map_process_temporal_statistics(process, keyword):
    """
    Map openEO (min_time, max_time, mean_time) to eoDataReader dict input.
    """

    dict_item = [
        {'name': 'add_band', 'bands': 1, 'file_num': 'all'},
        {'name': 'eo_function', 'group_bands': True,\
                 'f_input': {'f_name': 'temporal_statistics', 'stat_type': keyword + ';str'}}
        ]

    return dict_item


def csw_query(collection, spatial_extent, temporal_extent):
    """
    Retrieves a file list from the EODC CSW server according to the specified parameters.

    """

    csw = CatalogueServiceWeb(os.environ.get('CSW_SERVER'), timeout=300)
    constraints = []

    # Collection filter
    constraints.append(PropertyIsLike('apiso:ParentIdentifier', collection))
    # Spatial filter
    constraints.append(BBox(spatial_extent))
    # Temporal filter
    constraints.append(PropertyIsGreaterThan('apiso:TempExtent_begin', temporal_extent[0]))
    constraints.append(PropertyIsLessThan('apiso:TempExtent_end', temporal_extent[1]))

    # Run the query
    constraints = [constraints]
    csw.getrecords2(constraints=constraints, maxrecords=100)

    # Put found records in a variable (dictionary)
    records0 = csw.records

    # Put statistics about results in a variable
    #results = csw.results

    # Sort records
    records = []
    for record in records0:
        records.append(records0[record].references[0]['url'])
    records = sorted(records)

    return records
