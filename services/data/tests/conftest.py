
from os import environ, path

environ["ENV_FOR_DYNACONF"] = "unittest"

environ["OEO_CACHE_PATH"] = path.join(path.dirname(path.abspath(__file__)), "cache")
environ["OEO_DNS_URL"] = "http://0.0.0.0:3000/v1.0"

environ["OEO_IS_CSW_SERVER"] = "true"
environ["OEO_CSW_SERVER"] = "http://pycsw:8000"
environ["OEO_DATA_ACCESS"] = "public"
environ["OEO_GROUP_PROPERTY"] = "apiso:ParentIdentifier"
environ["OEO_WHITELIST"] = "s2b_prd_msil1c,s2a_prd_msil1c"

# unused in tests but must be there
environ["OEO_IS_CSW_SERVER_DC"] = "false"

# unused in tests but must be there
environ["OEO_IS_HDA_WEKEO"] = "false"
