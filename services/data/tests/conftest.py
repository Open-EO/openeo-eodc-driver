"""Prepares test environment.

Set all environment variables needed. As no fixture are required in this package none are defined here.
"""

import os
import sys
from os.path import abspath, dirname

root_dir = dirname(dirname(abspath(__file__)))
sys.path.append(root_dir)


os.environ["ENV_FOR_DYNACONF"] = "unittest"

os.environ["OEO_CACHE_PATH"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.environ["OEO_DNS_URL"] = "http://0.0.0.0:3000/v1.0"

os.environ["OEO_CSW_SERVER"] = "http://pycsw:8000"
os.environ["OEO_DATA_ACCESS"] = "public"
os.environ["OEO_GROUP_PROPERTY"] = "apiso:ParentIdentifier"
os.environ["OEO_WHITELIST"] = "s2b_prd_msil1c,s2a_prd_msil1c"

# unused in tests but must be there
os.environ["OEO_CSW_SERVER_DC"] = "http://pycsw:8001"
os.environ["OEO_DATA_ACCESS_DC"] = "public"
os.environ["OEO_GROUP_PROPERTY_DC"] = "apiso:ParentIdentifier"
os.environ["OEO_WHITELIST_DC"] = "s2b_prd_msil1c,s2a_prd_msil1c"
