"""

"""


from .map_utils import __map_default, __simple_process


def map_absolute(process):
    """
    
    """
    
    return __simple_process(process)


def map_clip(process):
    """
    
    """
    
    process_params = {}
    process_params['min'] = process['parameters']['min'] + ';float'
    process_params['max'] = process['parameters']['max'] + ';float'
    
    return __map_default(process, 'eo_clip', 'apply', **process_params)


def map_divide(process):
    """
    
    """
    
    return __map_default(process, 'eo_divide', 'reduce')
    
    
def map_linear_scale_range(process):
    """
    
    """
        
    if 'output_min' in process['parameters'].keys():
        output_min = process['parameters']['output_min']
    else:
        output_min = 0
    if 'output_max' in process['parameters'].keys():
        output_max = process['parameters']['output_max']
    else:
        output_max = 1
        
    process_params ={}
    process_params['input_min'] = process['parameters']['input_min'] + ';float'
    process_params['input_max'] = process['parameters']['input_max'] + ';float'
    process_params['output_min'] = process['parameters']['output_min'] + ';float'
    process_params['output_max'] = process['parameters']['output_max'] + ';float'
    
    return __map_default(process, 'eo_linear_scale_range', 'apply', **process_params)
    # 
    # dict_item = [
    #     {'name': 'add_band', 'bands': 'all', 'file_num': 'all'},
    #     {'name': 'apply', 'f_input': {
    #                                     'f_name': 'eo_linear_scale_range',
    #                                     'input_min': process['parameters']['input_min'] + ';float',
    #                                     'input_max': process['parameters']['input_max'] + ';float',
    #                                     'output_min': process['parameters']['output_min'] + ';float',
    #                                     'output_max': process['parameters']['output_max'] + ';float'
    #                                     }
    #     }
    #     ]
    # 
    # return dict_item
    
    
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
    # 
    # 
    # dict_item = [
    #     {'name': 'add_band', 'bands': 'all', 'file_num': 'all'},
    #     {'name': 'apply', 'f_input': {
    #                                     'f_name': 'eo_mod',
    #                                     'y': process['parameters']['y'] + ';float'
    #                                     }
    #     }
    #     ]
    # 
    # return dict_item
    

def map_multiply(process):
    """
    
    """
    
    process['f_input'] = __map_default(process, 'eo_multiply', 'reduce')
    
    return map_reduce(process)
    
    
def map_power(process):
    """
    
    """
    
    process_params = {}
    process_params['p'] = process['parameters']['p'] + ';float'
    
    return __map_default(process, 'eo_power', 'apply', **process_params)
    # 
    # dict_item = [
    #     {'name': 'add_band', 'bands': 'all', 'file_num': 'all'},
    #     {'name': 'apply', 'f_input': {
    #                                     'f_name': 'eo_power',
    #                                     'p': process['parameters']['p'] + ';float'
    #                                     }
    #     }
    #     ]
    # 
    # return dict_item
    
    
def map_product(process):
    """
    openEO process "product" is an alias for "multiply".
    
    """
    
    return __map_default(process, 'eo_multiply', 'reduce')
    
    
    #return map_reduce(process)
    
    
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
    # 
    # dict_item = [
    #     {'name': 'add_band', 'bands': 'all', 'file_num': 'all'},
    #     {'name': 'apply', 'f_input': {
    #                                     'f_name': 'eo_quantiles',
    #                                     'ignore_nodata': ignore_nodata + ';bool',
    #                                     'probabilities': probabilities + ';float',
    #                                     'q': q + ';float'
    #                                     }
    #     }
    #     ]
    # 
    # return dict_item
    
    
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
    
    return __map_default(process, 'eo_subtract', 'reduce')
    
    #return map_reduce(process)
    #return __map_default(process, 'eo_subtract')
    
    
def map_sum(process):
    """
    
    """
    
    return __map_default(process, 'eo_sum', 'reduce')
    
    #return map_reduce(process)
    
    

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
        p = str(process['parameters']['ignore_nodata'])
    else:
        p = None
    
    process_params = {}
    process_params['p'] = p + ';float'
    
    return __map_default(process, 'eo_exp', 'apply', **process_params)
    # 
    # dict_item = [
    #     {'name': 'apply', 'f_input': {
    #                                         'f_name': 'eo_exp',
    #                                         'p': process['parameters']['p'] + ';float'
    #                                         }
    #     }
    #     ]
    # 
    # return dict_item
    
    
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
    # 
    # dict_item = [
    #     {'name': 'apply', 'f_input': {
    #                                     'f_name': 'eo_log',
    #                                     'base': process['parameters']['base'] + ';float'
    #                                     }
    # }
    #     ]
    # 
    # return dict_item
    
    
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
    
    return __simple_process(process)
    

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
    
    
# #def __map_default(process, process_name, mapping, add_ignore_nodata=True):
# def __map_default(process, process_name, mapping, **kwargs):
#     """
#     Maps all processes which have only data input and ignore_nodata option.
#     """
# 
#     f_input = {}
#     f_input['f_name'] = process_name
#     for item in kwargs:
#         f_input[item] = kwargs[item]
# 
#     process['f_input'] = f_input
# 
#     # if 'ignore_nodata' in process['parameters'].keys():
#     #     ignore_nodata = str(process['parameters']['ignore_nodata'])
#     # else:
#     #     ignore_nodata = str(True)
#     # 
#     # if add_ignore_nodata:
#     #     process['f_input'] = {
#     #         'f_name': process_name,
#     #         'ignore_nodata': ignore_nodata + ';bool'
#     #     }
#     # else:
#     #     process['f_input'] = {'f_name': process_name}
# 
# 
#     if mapping == 'apply':
#         return map_apply(process)
#     elif mapping == 'reduce':
#         return map_reduce(process)
# 
#     # if add_ignore_nodata:
#     #     dict_item = [
#     #         {'name': 'apply', 'f_input': {
#     #                                         'f_name': process_name, 
#     #                                         'ignore_nodata': ignore_nodata + ';bool'
#     #                                         }
#     #         }
#     #         ]
#     # else:
#     #     dict_item = [
#     #         {'name': 'apply', 'f_input': {'f_name': process_name}}
#     #         ]
# 
#     #return f_input
# 
# 
# def __simple_process(process):
#     """
# 
#     """
# 
#     process_params = __set_ignore_data(process)
# 
#     return __map_default(process, process['id'], 'apply', **process_params)
# 
# 
# def __set_ignore_data(process):
#     """
#     Wrapper for common operation
#     """
# 
#     if 'ignore_nodata' in process['parameters'].keys():
#         ignore_nodata = str(process['parameters']['ignore_nodata'])
#     else:
#         ignore_nodata = str(True) # default
# 
#     process_params = {}
#     process_params['ignore_nodata'] = ignore_nodata + ';bool'
# 
#     return process_params
