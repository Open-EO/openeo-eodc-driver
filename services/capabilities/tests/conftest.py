# Triggered before every pytest run to add the directory so that the service can be found
# by pytest

import sys
from os import environ
from os.path import abspath, dirname

root_dir = dirname(dirname(abspath(__file__)))
sys.path.append(root_dir)

environ["OEO_GATEWAY_URL"] = "https://openeo.eodc.eu/"
