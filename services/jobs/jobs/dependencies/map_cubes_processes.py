"""

"""

from os import environ
from owslib.csw import CatalogueServiceWeb
from owslib.fes import PropertyIsLike, BBox, PropertyIsLessThan, PropertyIsGreaterThan


def map_load_collection(process):
    """
    Retrieves a file list and maps bbox and band filters to eoDataReaders.
    """

    # Get list of filepaths fro csw server
    filepaths = csw_query(collection=process['parameters']["id"],
                          spatial_extent=(
                              process['parameters']['spatial_extent']['south'],
                              process['parameters']['spatial_extent']['west'],
                              process['parameters']['spatial_extent']['north'],
                              process['parameters']['spatial_extent']['east']
                              ),
                          temporal_extent=process['parameters']["temporal_extent"]
                         )

    dict_item_list = []

    # Map band filter
    if 'bands' in process['parameters'].keys():
        dict_item = map_filter_bands(process)[0]
        dict_item_list.append(dict_item)

    # Map bbox filter
    if 'spatial_extent' in process['parameters'].keys():
        dict_item = map_filter_bbox(process)[0]
        dict_item_list.append(dict_item)

    return dict_item_list, filepaths
    

def map_filter_bands(process):
    """

    """

    dict_item_list = []

    if 'bands' in process['parameters'].keys():
        load_bands = process['parameters']['bands']
    elif 'names' in process['parameters'].keys():
        load_bands = process['parameters']['names']
    # elif 'wavelenghts' in process['args'].keys():
    #     # add this option
    else:
        load_bands = 'all'
    
    dict_item = {'name': 'filter_bands', 'bands': load_bands}
    dict_item_list.append(dict_item)

    return dict_item_list


def map_filter_bbox(process):
    """

    """

    # TODO support fields 'base' and 'height'

    dict_item_list = []

    if 'spatial_extent' in process['parameters'].keys():
        bbox = (process['parameters']['spatial_extent']['west'], process['parameters']['spatial_extent']['south'],\
                process['parameters']['spatial_extent']['east'], process['parameters']['spatial_extent']['north'])
        if 'crs' in process['parameters']['spatial_extent'].keys():
            crs_value = process['parameters']['spatial_extent']['crs']
        else:
            crs_value = 'EPSG:4326'
        dict_item = {'name': 'crop', 'bbox': bbox, 'crs': crs_value}
        dict_item_list.append(dict_item)

    return dict_item_list
    

#def map_reduce(process, reducer_name, reducer_dimension):
def map_reduce(process):
    """
    Reduce(self, f_input, dimension='time', per_file=False, in_memory=False):
    """
    
    if 'f_input' in process.keys():
        dict_item_list = [
                    {'name': 'reduce',
                    'dimension': process['reducer_dimension'],
                    'f_input': process['f_input']
                    }
                    ]
    else:
        # Add saving to vrt, else no vrt file is generated
        dict_item_list = [
            {'name': 'save_raster', 'format_type':'vrt'}
            ]
        # dict_item_list = [
        #             {'name': 'reduce',
        #             'dimension': process['reducer_dimension'],
        #             'f_input': {'f_name': 'eo_' + process['reducer_name']}
        #             }
        #             ]

    return dict_item_list
    

def map_apply(process):
    """
    Reduce(self, f_input, dimension='time', per_file=False, in_memory=False):
    """    
    
    dict_item_list = [
                {'name': 'apply',
                'f_input': {'f_name': 'eo_' + process['reducer_name']} # TODO change name, reducer is confusing here
                }
                ]

    return dict_item_list
    
    
def map_save_result(process):
    """

    """

    dict_item_list = [
                {'name': 'save_raster', 'format_type':  process['parameters']['format']}
                ]

    return dict_item_list


def csw_query(collection, spatial_extent, temporal_extent):
    """
    Retrieves a file list from the EODC CSW server according to the specified parameters.

    """

    csw = CatalogueServiceWeb(environ.get('CSW_SERVER'), timeout=300)
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
