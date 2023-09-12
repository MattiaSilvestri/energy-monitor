import os
import sys
import pytest
# add src to path to be able to run the tests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__name__), 'src')))
from utils.scraping import get_cpu_database
    

def test_get_cpu_database():
    # check that a json file has been saved in the data folder
    path = os.path.abspath(os.path.join(os.path.dirname(__name__), 'data'))
    json_fname = os.path.join(path, 'database_amd.json')
    assert isinstance(get_cpu_database(json_fname, 'AMD'), dict)
    assert os.path.isfile(json_fname)

    # repeat for intel
    path = os.path.abspath(os.path.join(os.path.dirname(__name__), 'data'))
    json_fname = os.path.join(path, 'database_intel.json')
    assert isinstance(get_cpu_database(json_fname, 'intel'), dict)
    assert os.path.isfile(json_fname)

