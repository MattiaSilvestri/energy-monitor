import requests
import yaml
import os


def get_request_co2signal(lon=None, lat=None, countrycode=None):
    """
    Perform a GET request to co2signal API.

    :param countrycode: The alpha-2 country code relative to the country where
    the user is located, defaults to None.
    :type countrycode: str
    :param lon: longitude coordinate retrived from public IP, defaults to None,
    :type lon: str
    :param lat: latitude coordinate retrived from public IP, defaults to None.
    :type lat: str
    :return: Dictionary containing the response
    :rtype: dict
    """

    # Read YAML file
    secrets_file_path = os.path.join(
        os.path.dirname(__file__).split("energy_monitor")[0], "config", "secrets.yml"
    )
    with open(secrets_file_path, "r") as stream:
        secrets = yaml.safe_load(stream)

    # Initialize the request
    url = "https://api.co2signal.com/v1/latest"
    headers = {"auth-token": secrets["API_keys"]["co2signal"]}

    if countrycode:
        if not isinstance(countrycode, str):
            raise ValueError("Country code must be a string")
        # get the list of countries
        req = requests.get("https://api.electricitymap.org/v3/zones")
        # Display country list
        code_list = [k for k in req.json()]
        if not countrycode in code_list:
            raise ValueError("Country code not found")
        params = {"countryCode": countrycode}
    else:
        params = {"lon": lon, "lat": lat}

    # Perform the API call
    req = requests.get(url, headers=headers, params=params)
    return req.json()


def get_location() -> dict:
    """
    Get latitude and longitude of the hosting machine.
    Reference: https://ipgeolocation.io/

    :return: dictionary with location information
    :rtype: dict
    """
    # Read YAML file
    secrets_file_path = os.path.join(
        os.path.dirname(__file__).split("energy_monitor")[0], "config", "secrets.yml"
    )
    with open(secrets_file_path, "r") as stream:
        secrets = yaml.safe_load(stream)

    # Initialize the request
    url = "https://api.ipgeolocation.io/ipgeo"
    params = {"apiKey": secrets["API_keys"]["ipgeolocation"]}

    # Perform the API call
    req = requests.get(url, params=params)

    return req.json()
