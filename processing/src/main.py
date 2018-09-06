from os import listdir
from eodatareaders.eo_data_reader import eoDataReader
from eofunctions.ndvi import ndvi

filename = '/eodc/products/copernicus.eu/s2a_prd_msil1c/2017/06/20/S2A_MSIL1C_20170620T100031_N0205_R122_T33UWP_20170620T100453.zip'

# IO options
io_opt = {
    'bands' : [4, 8],
    'output_folder' :  '/job_data/',
}

# warp options
warp_opt = {
    'projection' : 'EPSG:4326',
}

# eo functions
eo_func_opt = [
    {'name' : 'ndvi', 'input_bands' : [4, 8], 'group_bands' : True},
]

params = {'user_opt_IO' : io_opt, 'user_opt_warp' : warp_opt, 'user_opt_eo_functions' : eo_func_opt}
eo_object = eoDataReader(filename, params)
print('vrt files created.')

print(listdir(io_opt["output_folder"]))

# there should be vrt files in 'output_folder'