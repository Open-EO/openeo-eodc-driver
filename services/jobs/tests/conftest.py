# Triggered before every pytest run to add the directory so that the service can be found
# by pytest

import sys
from os.path import dirname
from os.path import abspath
from os import environ

environ['AIRFLOW_HOST'] = 'TEST'

root_dir = dirname(dirname(abspath(__file__)))
sys.path.append(root_dir)
