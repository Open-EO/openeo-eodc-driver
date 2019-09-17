"""

"""


try:
    from map_utils import __map_default, __simple_process, __set_extra_values
except:
    from .map_utils import __map_default, __simple_process, __set_extra_values


def map_absolute(process):
    """
    
    """
    
    return __simple_process(process)


def map_clip(process):
    """
    
    """
    
    param_dict = {'min': 'float', 'max': 'float'}
    process_params = __get_process_params(process, param_dict)
    
    return __map_default(process, 'eo_clip', 'apply', **process_params)


def map_divide(process):
    """
    
    """
    
    process_params = __set_extra_values(process, add_extra_idxs=True)
    
    return __map_default(process, 'eo_divide', 'reduce', **process_params)
    
    
def map_linear_scale_range(process):
    """
    
    """
    
    param_dict = {'input_min': 'float', 'input_max': 'float', 'output_min': 'float', 'output_max': 'float'}
    process_params = __get_process_params(process, param_dict)
    if not process_params['output_min']:
        process_params['output_min'] = 0
    if not process_params['output_max']:
        process_params['output_max'] = 1
    
    return __map_default(process, 'eo_linear_scale_range', 'apply', **process_params)
    
    
def map_max(process):
    """
    
    """
    
    return __map_default(process, 'eo_max', 'reduce')
    
    
def map_min(process):
    """
    
    """
    
    return __map_default(process, 'eo_min', 'reduce')
    
    #return map_reduce(process)
    
    
def map_mean(process):
    """
    
    """
    
    return __map_default(process, 'eo_mean', 'reduce')
    

def map_median(process):
    """
    
    """
    
    return __map_default(process, 'eo_median', 'reduce')
    
    
def map_mod(process):
    """
    
    """
    
    process_params = {}
    process_params['y'] = process['parameters']['y'] + ';float'
    
    return __map_default(process, 'eo_mod', 'apply', **process_params)


def map_multiply(process):
    """
    
    """
    
    process_params = __set_extra_values(process)
    
    return __map_default(process, 'eo_multiply', 'reduce', **process_params)
    
    
def map_power(process):
    """
    
    """
    
    process_params = {}
    process_params['p'] = process['parameters']['p'] + ';float'
    
    return __map_default(process, 'eo_power', 'apply', **process_params)
    
    
def map_product(process):
    """
    openEO process "product" is an alias for "multiply".
    
    """
    
    process_params = __set_extra_values(process)
    
    return __map_default(process, 'eo_multiply', 'reduce', **process_params)
    
    
def map_quantiles(process):
    """
    
    """
    
    if 'probabilities' in process['parameters'].keys():
        probabilities = process['parameters']['probabilities']
    else:
        probabilities = None
    if 'q' in process['parameters'].keys():
        q = process['parameters']['q']
    else:
        q = None
        
    process_params = set_ignore_data(process)
    process_params['probabilities'] =  probabilities + ';float'
    process_params['q'] = q + ';float'
    
    return __map_default(process, 'eo_quantiles', 'apply', **process_params)
    
    
def map_sd(process):
    """
    
    """
    
    return __map_default(process, 'eo_sd', 'reduce')
    
    
def map_sgn(process):
    """
    
    """
    
    return __simple_process(process)
    
    
def map_sqrt(process):
    """
    
    """
    
    return __simple_process(process)
    
    
def map_subtract(process):
    """
    
    """
    
    process_params = __set_extra_values(process, add_extra_idxs=True)
    
    return __map_default(process, 'eo_subtract', 'reduce', **process_params)
    
    
def map_sum(process):
    """
    
    """
    
    process_params = __set_extra_values(process)
        
    return __map_default(process, 'eo_sum', 'reduce', **process_params)    
    

def map_variance(process):
    """
    
    """
    
    return __map_default(process, 'eo_variance', 'reduce')
    
    
def map_e(process):
    """
    
    """
    
    return __simple_process(process)
    
    
def map_pi(process):
    """
    
    """
    
    return __simple_process(process)
    
    
# def map_cummax(process):
#     """
# 
#     """
# 
#     # needs apply_dimension
# 
#     return __map_default(process, 'eo_cummax')
# 
# 
# def map_cumproduct(process):
#     """
# 
#     """
#     # needs apply_dimension
#     return __map_default(process, 'eo_cumproduct')
# 
# 
# def map_cumsum(process):
#     """
# 
#     """
#     # needs apply_dimension
#     return __map_default(process, 'eo_cummsum')
    
    
def map_exp(process):
    """
    
    """
    
    if 'p' in process['parameters'].keys():
        p = str(process['parameters']['p'])
    else:
        p = None
    
    process_params = {}
    process_params['p'] = p + ';float'
    
    return __map_default(process, 'eo_exp', 'apply', **process_params)
    
    
def map_ln(process):
    """
    
    """
    
    return __simple_process(process)
    
    
def map_log(process):
    """
    
    """
    
    if 'base' in process['parameters'].keys():
        base = str(process['parameters']['ignore_nodata'])
    else:
        base = None
    
    process_params = {}
    process_params['base'] = ignore_nodata + ';float'
    
    return __map_default(process, 'eo_log', 'apply', **process_params)
    
    
def map_ceil(process):
    """
    
    """
    
    return __simple_process(process)
    
    
def map_floor(process):
    """
    
    """
    
    return __simple_process(process)
    
    
def map_int(process):
    """
    
    """
    
    return __simple_process(process)
    
    
def map_round(process):
    """
    
    """
    
    if 'p' in process['parameters'].keys():
        p = str(process['parameters']['p'])
    else:
        p = None
    
    process_params = {}
    process_params['p'] = p + ';int'
    
    return __map_default(process, 'eo_round', 'apply', **process_params)
    

def map_arccos(process):
    """
    
    """
        
    return __simple_process(process)
    
def map_arcosh(process):
    """
    
    """
        
    return __simple_process(process)
    

def map_arcsin(process):
    """
    
    """
        
    return __simple_process(process)
    

def map_arsinh(process):
    """
    
    """
        
    return __simple_process(process)
    
    
def map_arctan(process):
    """
    
    """
        
    return __simple_process(process)
    
    
def map_arctan2(process):
    """
    
    """
        
    return __simple_process(process)
    
    
def map_artanh(process):
    """
    
    """
        
    return __simple_process(process)
    
    
def map_cos(process):
    """
    
    """
        
    return __simple_process(process)
    

def map_cosh(process):
    """
    
    """
    
    return __simple_process(process)
    
    
def map_sin(process):
    """
    
    """
    
    return __simple_process(process)
    
    
def map_sinh(process):
    """
    
    """
    
    return __simple_process(process)
    

def map_tan(process):
    """
    
    """
    
    return __simple_process(process)
    
    
def map_tanh(process):
    """
    
    """
    
    return __simple_process(process)
