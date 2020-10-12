"""Prepares test environment.

Set all environment variables needed. As no fixture are required in this package none are defined here.
"""

import os
import sys
from os.path import abspath, dirname

root_dir = dirname(dirname(abspath(__file__)))
sys.path.append(root_dir)

from os import environ, path

environ["ENV_FOR_DYNACONF"] = "unittest"
os.environ["OEO_CACHE_PATH"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
environ["OEO_CACHE_PATH"] = path.join(path.dirname(path.abspath(__file__)), "cache")
environ["OEO_DNS_URL"] = "http://0.0.0.0:3000/v1.0"

environ["OEO_IS_CSW_SERVER"] = "true"
environ["OEO_CSW_SERVER"] = "http://pycsw:8000"
environ["OEO_DATA_ACCESS"] = "public"
environ["OEO_GROUP_PROPERTY"] = "apiso:ParentIdentifier"
environ["OEO_WHITELIST"] = "s2b_prd_msil1c,s2a_prd_msil1c"

# unused in tests but must be there
environ["OEO_IS_CSW_SERVER_DC"] = "true"
environ["OEO_CSW_SERVER_DC"] = "https://csw-acube.eodc.eu"
environ["OEO_DATA_ACCESS_DC"] = "acube"
environ["OEO_GROUP_PROPERTY_DC"] = "eodc:variable_name"
environ["OEO_WHITELIST_DC"] = "SIG0"

# unused in tests but must be there
environ["OEO_IS_HDA_WEKEO"] = "true"
environ["OEO_WEKEO_API_URL"] = "https://wekeo-broker.apps.mercator.dpi.wekeo.eu/databroker"
environ["OEO_WHITELIST_WEKEO"] = "EO:ESA:DAT:SENTINEL-5P:TROPOMI:L2__NO2___"
