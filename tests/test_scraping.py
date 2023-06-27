import os
import sys
import pytest
# add src to path to be able to run the tests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__name__), 'src')))
from utils.scraping import scrape_tdp_intel, get_AMD_database


def test_scrape_tdp_intel():
    # Check that the function raises a value error for different cases other than input string
    with pytest.raises(ValueError):
        scrape_tdp_intel("Unknown CPU Name")
    with pytest.raises(ValueError):
        scrape_tdp_intel(1234)
    with pytest.raises(ValueError):    
        scrape_tdp_intel("")
    with pytest.raises(ValueError):
        scrape_tdp_intel(None)
    # check that the function returns a float
    assert isinstance(scrape_tdp_intel('Intel(R) Core(TM) i7-8569U CPU @ 2.80GHz'), float)
    # check that the function returns a float greater than zero
    assert scrape_tdp_intel('Intel(R) Core(TM) i7-8569U CPU @ 2.80GHz') > 0.0
    

def test_get_AMD_database():
    # check that a json file has been saved in the data folder
    path = os.path.abspath(os.path.join(os.path.dirname(__name__), 'data'))
    json_fname = os.path.join(path, 'tableExport.json')
    assert os.path.isfile(json_fname)

