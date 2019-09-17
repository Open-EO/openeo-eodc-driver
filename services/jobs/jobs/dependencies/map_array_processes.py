"""

"""


try:
    from map_utils import __map_default
except:
    from .map_utils import __map_default


def map_array_element(process):
    """
    
    """
    
    process_params = {}
    process_params['index'] = str(process['parameters']['index']) + ';int'
    process_params['per_file'] = True
    
    return __map_default(process, 'eo_array_element', 'reduce', **process_params)
