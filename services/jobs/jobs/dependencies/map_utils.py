"""

"""


from os import path
import inspect
import importlib


#def __map_default(process, process_name, mapping, add_ignore_nodata=True):
def __map_default(process, process_name, mapping, **kwargs):
    """
    Maps all processes which have only data input and ignore_nodata option.
    """
    
    f_input = {}
    f_input['f_name'] = process_name
    for item in kwargs:
        f_input[item] = kwargs[item]
        
    process['f_input'] = f_input
    
    # if 'ignore_nodata' in process['parameters'].keys():
    #     ignore_nodata = str(process['parameters']['ignore_nodata'])
    # else:
    #     ignore_nodata = str(True)
    # 
    # if add_ignore_nodata:
    #     process['f_input'] = {
    #         'f_name': process_name,
    #         'ignore_nodata': ignore_nodata + ';bool'
    #     }
    # else:
    #     process['f_input'] = {'f_name': process_name}
        
        
    if mapping == 'apply':
        return map_apply(process)
    elif mapping == 'reduce':
        return map_reduce(process)
    
    # if add_ignore_nodata:
    #     dict_item = [
    #         {'name': 'apply', 'f_input': {
    #                                         'f_name': process_name, 
    #                                         'ignore_nodata': ignore_nodata + ';bool'
    #                                         }
    #         }
    #         ]
    # else:
    #     dict_item = [
    #         {'name': 'apply', 'f_input': {'f_name': process_name}}
    #         ]

    #return f_input
    
    
def __simple_process(process):
    """
    
    """
    
    process_params = __set_ignore_data(process)
    
    return __map_default(process, process['id'], 'apply', **process_params)
    

def __set_ignore_data(process):
    """
    Wrapper for common operation
    """
    
    if 'ignore_nodata' in process['parameters'].keys():
        ignore_nodata = str(process['parameters']['ignore_nodata'])
    else:
        ignore_nodata = str(True) # default
    
    process_params = {}
    process_params['ignore_nodata'] = ignore_nodata + ';bool'
    
    return process_params


def set_output_folder(root_folder, folder_name, options=[]):
    """
    Appends folder to options.
    """

    # Set output_folder for this operation
    dict_item = {'name': 'set_output_folder',\
                 'folder_name': root_folder + path.sep + folder_name + path.sep,\
                 'absolute_path': '1;int'}


    return options.append(dict_item)
    

def get_mapped_processes():
    """
    Returns the openeo processes mapped and available on the back-end, sorted alphabetically.
    """
    
    modules = ['map_cubes_processes',
               'map_math_processes',
               'map_veg_indices_processes',
               'map_arrays_processes']
    
    processes = []
    for module_name in modules:
        module = importlib.import_module(module_name)
        funcs = inspect.getmembers(module, inspect.isfunction)
        for func in funcs:
            func_name = func[0]
            # func_callable = func[1] # just for clarity
            if func_name.startswith('map_'):
                processes.append(func_name.replace('map_', ''))
    
    return sorted(processes)
        
        
        
    
