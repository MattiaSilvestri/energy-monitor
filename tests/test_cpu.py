import os
import sys
import pytest
# add src to path to be able to run the tests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__name__), 'src')))
from utils.cpu import get_cpu_info, get_cpu_usage, get_cpu_tdp


def test_get_cpu_info():
    # Call the function and check the result
    result = get_cpu_info()
    assert isinstance(result, str)
    assert "amd" in result.lower() or "intel" in result.lower()


def test_get_cpu_usage():
    # Call the function and check the result
    result = get_cpu_usage(1.0)
    assert isinstance(result, float)
    assert result < 100.0


def test_get_cpu_tdp():
    # Call the function with a known CPU name
    cpu_name = 'Intel(R) Core(TM) i7-8569U CPU @ 2.80GHz'
    tdp = get_cpu_tdp(cpu_name)

    # Check that the result is a float
    assert isinstance(tdp, float)

    # Check that the result is greater than zero
    assert tdp > 0.0 
    
    # check that a json file has been saved in the data folder
    path = os.path.join(os.path.dirname(__file__).split("energy-monitor")[0], 'energy-monitor', 'data')
    json_fname = os.path.join(path, 'cpu_tdp.json')
    assert os.path.isfile(json_fname)