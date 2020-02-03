# Triggered before every pytest run to add the directory so that the service can be found
# by pytest

import sys
from os.path import dirname
from os.path import abspath

root_dir = dirname(dirname(abspath(__file__)))
sys.path.append(root_dir)