import os

os.environ["ENV_FOR_DYNACONF"] = "unittest"

os.environ["OEO_CACHE_PATH"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.environ["OEO_DNS_URL"] = "http://0.0.0.0:3000/v1.0"

os.environ["OEO_IS_CSW_SERVER"] = "true"
os.environ["OEO_CSW_SERVER"] = "http://pycsw:8000"
os.environ["OEO_DATA_ACCESS"] = "public"
os.environ["OEO_GROUP_PROPERTY"] = "apiso:ParentIdentifier"
os.environ["OEO_WHITELIST"] = "s2b_prd_msil1c,s2a_prd_msil1c"

# unused in tests but must be there
os.environ["OEO_IS_CSW_SERVER_DC"] = "false"

# unused in tests but must be there
os.environ["OEO_IS_HDA_WEKEO"] = "false"
