import energymonitor as em
from energymonitor import api_calls
from energymonitor import cli

def main(args = None, country_code = None) -> None:
    """Function to run the core of the app: compare CPU usage with CO2 emissions"""

    # Use manual country code if set, otherwise use geolocalizaion
    if args:
        # Get location
        geolocation = api_calls.get_location()
        lon = geolocation['longitude']
        lat = geolocation['latitude']

        # Retrieve data from Co2Signal API
        co2data = api_calls.get_request_co2signal(lon, lat)
        country_code = co2data['countryCode']
    elif country_code:
        # Retrieve data from Co2Signal API
        co2data = api_calls.get_request_co2signal(countrycode=country_code)

    try:
        # Extract relevant measures
        print('\nRetrieving Co2Signal data...')
        carbon_intensity = co2data['data']['carbonIntensity']
        carbon_intensity_unit = co2data['units']['carbonIntensity']
        fossil_percentage = round(co2data['data']['fossilFuelPercentage'],2)
        print("- Selected Country: {0} \n- Carbon Intensity: {1} ({2}) \n- Percentage of fossil fuel: {3}%".format(country_code, carbon_intensity, carbon_intensity_unit, fossil_percentage))

        # Retrieve cpu info
        print('\nRetrieving CPU data...')
        cpu_info = em.get_cpu_info()
        cpu_usage = em.get_cpu_usage(10) #it seems too low to be true!
        print("- Current CPU: {0} \n- CPU usage during last 10s: {1}%".format(cpu_info, cpu_usage))
    except KeyError:
        print('Sorry, your country is not present in the Electricity Map ' +
              'database, it is therefore not possible to retrieve CO2 emissions data.')

