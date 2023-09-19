import os
import sys
import pytest
# add src to path to be able to run the tests
sys.path.append(os.path.join(os.path.dirname(__file__).split('tests')[0], 'src'))
from utils.scraping import get_cpu_database
    

def test_get_cpu_database():
    # check that a json file has been saved in the data folder
    json_fname = os.path.join(os.path.dirname(__file__).split("tests")[0], 'data', 'database_amd.json')
    assert isinstance(get_cpu_database(json_fname, 'AMD'), dict)
    assert os.path.isfile(json_fname)

    # repeat for intel
    json_fname = os.path.join(os.path.dirname(__file__).split("tests")[0], 'data', 'database_intel.json')
    assert isinstance(get_cpu_database(json_fname, 'intel'), dict)
    assert os.path.isfile(json_fname)
