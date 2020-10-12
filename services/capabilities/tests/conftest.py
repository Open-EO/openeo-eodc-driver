"""Sets up paths and environment variables to run tests.

This module is triggered before every pytest run to add the directory so that the service can be found by pytest.
Additionally required environment variables can be set here but currently the service requires none.
"""
import os
import sys
from os.path import abspath, dirname

root_dir = dirname(dirname(abspath(__file__)))
sys.path.append(root_dir)

os.environ["ENV_FOR_DYNACONF"] = "unittest"
