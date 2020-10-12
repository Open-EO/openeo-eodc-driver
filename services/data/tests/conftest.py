"""Prepares test environment.

Set all environment variables needed. As no fixture are required in this package none are defined here.
"""

import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

os.environ["ENV_FOR_DYNACONF"] = "unittest"
os.environ["OEO_CACHE_PATH"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.environ["OEO_CACHE_PATH"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.environ["OEO_DNS_URL"] = "http://0.0.0.0:3000/v1.0"

os.environ["OEO_IS_CSW_SERVER"] = "true"
os.environ["OEO_CSW_SERVER"] = "http://pycsw:8000"
os.environ["OEO_DATA_ACCESS"] = "public"
os.environ["OEO_GROUP_PROPERTY"] = "apiso:ParentIdentifier"
os.environ["OEO_WHITELIST"] = "s2b_prd_msil1c,s2a_prd_msil1c"

# unused in tests but must be there
os.environ["OEO_IS_CSW_SERVER_DC"] = "true"
os.environ["OEO_CSW_SERVER_DC"] = "https://csw-acube.eodc.eu"
os.environ["OEO_DATA_ACCESS_DC"] = "acube"
os.environ["OEO_GROUP_PROPERTY_DC"] = "eodc:variable_name"
os.environ["OEO_WHITELIST_DC"] = "SIG0"

# unused in tests but must be there
os.environ["OEO_IS_HDA_WEKEO"] = "true"
os.environ["OEO_WEKEO_API_URL"] = "https://wekeo-broker.apps.mercator.dpi.wekeo.eu/databroker"
os.environ["OEO_DATA_ACCESS_WEKEO"] = "wekeo"
os.environ["OEO_WHITELIST_WEKEO"] = "EO:ESA:DAT:SENTINEL-5P:TROPOMI:L2__NO2___"
os.environ["OEO_WEKEO_STORAGE"] = "/usr/local/airflow/wekeo_storage"
