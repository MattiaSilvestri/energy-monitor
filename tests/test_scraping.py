import os
import sys
import pytest
# add src to path to be able to run the tests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__name__), 'src')))
from utils.scraping import get_cpu_database
    

def test_get_cpu_database():
    # 
    assert isinstance(get_cpu_database('AMD Ryzen 7 5700U with Radeon Graphics'), dict)
    # check that a json file has been saved in the data folder
    path = os.path.abspath(os.path.join(os.path.dirname(__name__), 'data'))
    json_fname = os.path.join(path, 'database_amd.json')
    assert os.path.isfile(json_fname)

    assert isinstance(get_cpu_database('Intel(R) Core(TM) i7-8569U CPU @ 2.80GHz'), dict)
    # check that a json file has been saved in the data folder
    path = os.path.abspath(os.path.join(os.path.dirname(__name__), 'data'))
    json_fname = os.path.join(path, 'database_intel.json')
    assert os.path.isfile(json_fname)

