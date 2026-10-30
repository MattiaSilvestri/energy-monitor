import os
import sys
import pytest
from energy_monitor.utils.cpu import get_cpu_info, get_cpu_usage, get_cpu_tdp
from energy_monitor.utils.paths import user_data_file


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
    
    # check that the tdp has been saved in the user data file
    assert user_data_file().is_file()
