import requests
import yaml
import os
import sys

from energy_monitor.utils.paths import secrets_file

# Name of each API key in secrets.yml and the environment variables that can override it
API_KEYS = {
    "co2signal": ("ELECTRICITYMAPS_API_KEY", "CO2SIGNAL_API_KEY"),
    "ipgeolocation": ("IPGEOLOCATION_API_KEY",),
}


def get_api_key(name: str) -> str:
    """
    Return the API key for the given service, looking first in the environment
    variables and then in the user secrets.yml file.

    :param name: name of the service, one of API_KEYS
    :type name: str
    :return: API key
    :rtype: str
    """
    for env_var in API_KEYS[name]:
        if os.environ.get(env_var):
            return os.environ[env_var]

    fname = secrets_file()
    if fname.is_file():
        with open(fname, "r") as stream:
            secrets = yaml.safe_load(stream) or {}
        key = (secrets.get("API_keys") or {}).get(name)
        if key:
            return key

    sys.exit(
        f"Missing API key for '{name}'.\n"
        f"Run 'energy-monitor --set-api-keys' to store it in {fname},\n"
        f"or set the {API_KEYS[name][0]} environment variable."
    )


def save_api_keys(keys: dict) -> None:
    """
    Store the given API keys in the user secrets.yml file, keeping the existing ones.

    :param keys: dictionary {service name: API key}
    :type keys: dict
    """
    fname = secrets_file()
    secrets: dict = {}
    if fname.is_file():
        with open(fname, "r") as stream:
            secrets = yaml.safe_load(stream) or {}
    secrets.setdefault("API_keys", {})
    secrets["API_keys"].update({k: v for k, v in keys.items() if v})

    with open(fname, "w") as stream:
        yaml.safe_dump(secrets, stream)
    os.chmod(fname, 0o600)


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

    # Initialize the request (CO2 Signal has been merged into Electricity Maps)
    base_url = "https://api.electricitymaps.com/v3"
    headers = {"auth-token": get_api_key("co2signal")}

    if countrycode:
        if not isinstance(countrycode, str):
            raise ValueError("Country code must be a string")
        # get the list of countries
        req = requests.get(f"{base_url}/zones")
        # Display country list
        code_list = [k for k in req.json()]
        if not countrycode in code_list:
            raise ValueError("Country code not found")
        params = {"zone": countrycode}
    else:
        params = {"lon": lon, "lat": lat}

    # Perform the API calls
    intensity = requests.get(
        f"{base_url}/carbon-intensity/latest", headers=headers, params=params
    )
    intensity.raise_for_status()
    breakdown = requests.get(
        f"{base_url}/power-breakdown/latest", headers=headers, params=params
    )
    breakdown.raise_for_status()
    intensity_data = intensity.json()
    breakdown_data = breakdown.json()

    fossil_free = breakdown_data.get("fossilFreePercentage")
    fossil_percentage = None if fossil_free is None else float(100 - fossil_free)

    # Keep the response format of the legacy co2signal API
    return {
        "status": "ok",
        "countryCode": intensity_data["zone"],
        "data": {
            "datetime": intensity_data["datetime"],
            "carbonIntensity": intensity_data["carbonIntensity"],
            "fossilFuelPercentage": fossil_percentage,
        },
        "units": {"carbonIntensity": "gCO2eq/kWh"},
    }


def get_location() -> dict:
    """
    Get latitude and longitude of the hosting machine.
    Reference: https://ipgeolocation.io/

    :return: dictionary with location information
    :rtype: dict
    """
    # Initialize the request
    url = "https://api.ipgeolocation.io/ipgeo"
    params = {"apiKey": get_api_key("ipgeolocation")}

    # Perform the API call
    req = requests.get(url, params=params)

    return req.json()
