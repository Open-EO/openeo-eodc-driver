"""

"""


def map_array_element(process):
    """
    
    """
    
    # dict_item = [
    #         {'name': 'apply', 'f_input': {
    #             'f_name': 'eo_array_element',
    #             'dimension': process['reducer_dimension'],
    #             'index': str(process['parameters']['index']) + ';int'
    #             }
    #         }
    #         ]
    
    dict_item_list = []
            
    dict_item = {'name': 'filter_index',
                 'index': str(process['parameters']['index']) + ';int',
                 'dimension_name': process['reducer_dimension']}
    dict_item_list.append(dict_item)
    
    # Add saving to vrt, else no vrt file is generated
    dict_item = {'name': 'save_raster', 'format_type':'vrt'}
    dict_item_list.append(dict_item)

    return dict_item_list
