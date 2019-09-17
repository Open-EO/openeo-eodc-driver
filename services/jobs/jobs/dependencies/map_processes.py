"""
A module dostring.
"""

try:
    from map_cubes_processes import *
    from map_math_processes import *
    from map_veg_indices_processes import *
    from map_array_processes import *
    from map_utils import set_output_folder
except:
    from .map_cubes_processes import *
    from .map_math_processes import *
    from .map_veg_indices_processes import *
    from .map_array_processes import *
    from .map_utils import set_output_folder


def map_process(process, process_name, process_id, root_folder, 
                reducer_name=None, reducer_dimension=None,
                options=None):
    """
    Entry point.
    """
    
    # Match multiple names for load_collection (for backward compatibility)
    if process['process_id'] in ('get_data', 'get_collection'):
        process['process_id'] = 'load_collection'

    if not options:
        options = []

    filepaths = None

    # Add/set output folder
    set_output_folder(root_folder, process_id, options)
            
    if reducer_name:
        process['reducer_name'] = reducer_name
    if reducer_dimension:
        process['reducer_dimension'] = reducer_dimension
        
    dict_items = eval("map_" + process['process_id'] + "(process)")
    
    if isinstance(dict_items, tuple):
        filepaths = dict_items[1]
        dict_items = dict_items[0]

    if not isinstance(dict_items, list):
        dict_items = [dict_items]
    for dict_item in dict_items:
        options.append(dict_item)

    return options, filepaths
