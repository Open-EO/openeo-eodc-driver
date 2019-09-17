"""

"""


from os import path
import inspect
import importlib
from numbers import Number

try:
    from map_cubes_processes import map_apply, map_reduce
except:
    from .map_cubes_processes import map_apply, map_reduce


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
        
    if mapping == 'apply':
        return map_apply(process)
    elif mapping == 'reduce':
        return map_reduce(process)
    
    
def __simple_process(process):
    """
    
    """
    
    process_params = __get_process_params(process, {'ignore_data': 'bool'})
    
    return __map_default(process, process['id'], 'apply', **process_params)
    

def __get_process_params(process, param_dict):
    """
    params_list is a dict, e.g.: {'ignore_data': 'bool', 'p': 'int'}
    """
    
    process_params = {}
    for param in param_dict:
        if param in process['parameters'].keys():
            process_params[param] = str(process['parameters'][param]) + ';' + param_dict[param]
    
    return process_params
    

def __set_extra_values(process, add_extra_idxs=False):
    
    extra_values = []
    extra_idxs = []
    for k, item in enumerate(process['parameters']['data']):
        if isinstance(item, Number):
            extra_values.append(item)
            if add_extra_idxs:
                extra_idxs.append(k)            
    
    process_params = {}
    if extra_values:
        process_params['extra_values'] = str(extra_values) + ';list'
        if add_extra_idxs:
            process_params['extra_idxs'] = str(extra_idxs) + ';list'
    
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
        
        
        
    
