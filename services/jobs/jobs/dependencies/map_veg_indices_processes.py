"""

"""


def map_ndvi(process):
    """
    Map openEO NDVI to eoDataReader dict input.
    """
    
    # NB use "nir" and "red", instead of numbers
    dict_item = [
        {'name': 'filter_bands', 'bands': [4, 8]},
        {'name': 'reduce', 'f_input': {'f_name' : 'eo_ndvi'},
         'dimension': 'band', 'per_file': True}
        ]

    return dict_item
