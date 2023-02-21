import requests

def get_request_co2signal(countrycode):
    """
    Perform a GET request to co2signal API.

    :param countrycode: The alpha-2 country code relative to the country where the user is located
    :type countrycode: str
    :return: Dictionary containing the response
    :rtype: dict
    """

    # Initialize the request
    url = 'https://api.co2signal.com/v1/latest'
    headers = {'auth-token': 'NjqWpnG2yaPL3gIaP9pPQeoFshLGd5Qo'}
    params = {'countryCode': countrycode}

    # Perform the API call
    req = requests.get(url, headers=headers, params=params)
    return req.json()