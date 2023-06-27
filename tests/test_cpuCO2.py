import os
import sys
import pytest
# add src to path to be able to run the tests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__name__), 'src')))
from core.cpuCO2 import combine_cpu_CO2, get_interval_emissions
from utils.cpu import get_cpu_info, get_cpu_tdp
from utils.api_calls import get_request_co2signal


def test_combine_cpu_CO2():
    # check that it raises a type error if different values are passed
    with pytest.raises(TypeError):
        combine_cpu_CO2("1",1,1,1)
    with pytest.raises(TypeError):
        combine_cpu_CO2(1,"1",1,1)
    with pytest.raises(TypeError):
        combine_cpu_CO2(1,1,"1",1)
    with pytest.raises(TypeError):
        combine_cpu_CO2(1,1,1,"1")
    # test that the function returns a number
    assert isinstance(combine_cpu_CO2(1.,1,1,1.), float)
    # test that the function returns a number larger than 0
    assert combine_cpu_CO2(10,1,15,490) > 0


def test_get_interval_emissions():
    # check that it raises a type error if different values are passed
    with pytest.raises(TypeError):
        get_interval_emissions("1",1,1)
    with pytest.raises(TypeError):
        get_interval_emissions(1,"1",1)
    with pytest.raises(TypeError):
        get_interval_emissions(1,1,"1")
        
    # test that the function returns a number
    assert isinstance(get_interval_emissions(1,1,1), float)
    # test that the function returns a number larger than 0
    assert get_interval_emissions(15, 490, 1) > 0
