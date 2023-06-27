import os
import sys
import pytest
# add src to path to be able to run the tests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__name__), 'src')))
from utils.api_calls import get_location, get_request_co2signal


def test_get_location():
    # Get location
    geolocation = get_location()
    # Check that the dictionary is not empty
    assert geolocation
    # Check that the dictionary contains the expected keys
    assert 'longitude' in geolocation
    assert 'latitude' in geolocation
    # Check that the dictionary contains the expected values
    assert isinstance(geolocation['longitude'], str)
    assert isinstance(geolocation['latitude'], str)
    assert float(geolocation['latitude'])
    assert float(geolocation['longitude'])
    

def test_get_request_co2signal():
    # check that the function returns value errors if no country code or coordinates are provided
    with pytest.raises(ValueError):
        get_request_co2signal()
    # check that the function returns value errors if the country code is not an alpha-2 code
    with pytest.raises(ValueError):
        get_request_co2signal(countrycode='ABC')
    # check that the function returns value errors if the coordinates are not int or float
    with pytest.raises(ValueError):
        get_request_co2signal(lon=1, lat=1)

    # check the output of the function 
    for input in [('IT'), ('12.5674', '41.8719')]:
        if len(input) == 1:
            output = get_request_co2signal(countrycode='IT')
        else:
            output = get_request_co2signal(lon='12.5674', lat='41.8719')

        assert isinstance(output, dict)
        # check that the dictionary contains the expected keys
        assert 'countryCode' in output
        assert 'data' in output
        assert 'units' in output
        assert 'status' in output
        # check that the dictionary contains the expected values
        assert isinstance(output['countryCode'], str)
        assert isinstance(output['data'], dict)
        assert isinstance(output['data']['carbonIntensity'], int)
        assert isinstance(output['data']['fossilFuelPercentage'], float)
        assert isinstance(output['units'], dict)
        assert isinstance(output['units']['carbonIntensity'], str)
        assert isinstance(output['status'], str)
        # check that the country code is correct
        assert 'IT' in output['countryCode']

