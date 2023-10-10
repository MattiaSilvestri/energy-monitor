import os
import sys
import pytest
# add src to path to be able to run the tests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__name__), 'src')))
from core.cpuCO2 import combine_cpu_CO2, get_interval_emissions


def test_combine_cpu_CO2():
    # test that the function returns a number
    assert isinstance(combine_cpu_CO2(1.,1.,1.,1), float)
    # test that the function returns a number larger than 0
    assert combine_cpu_CO2(10.,1.,15.,490) > 0


def test_get_interval_emissions():    
    # test that the function returns a float
    assert isinstance(get_interval_emissions(1.0,1,1), float)
    # test that the function returns a number larger than 0
    assert get_interval_emissions(28., 500, 1) >= 0
