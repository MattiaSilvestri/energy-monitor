import os
import sys
import pytest
from energy_monitor.utils.scraping import get_cpu_database
    

def test_get_cpu_database(tmp_path):
    # check that a json file has been saved in the data folder
    json_fname = os.path.join(tmp_path, 'data', 'database_amd.json')
    assert isinstance(get_cpu_database(json_fname, 'amd'), dict)
    assert os.path.isfile(json_fname)

    # repeat for intel
    json_fname = os.path.join(tmp_path, 'data', 'database_intel.json')
    assert isinstance(get_cpu_database(json_fname, 'intel'), dict)
    assert os.path.isfile(json_fname)


if __name__ == '__main__':
    pytest.main([__file__])