import os

os.environ["ENV_FOR_DYNACONF"] = "unittest"

os.environ["OEO_CACHE_PATH"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.environ["OEO_CSW_SERVER"] = "http://pycsw:8000"
os.environ["OEO_DNS_URL"] = "http://0.0.0.0:3000/v1.0"
