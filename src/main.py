import energymonitor as em
from energymonitor import api_calls
from energymonitor import user_inputs

country_code = user_inputs.get_country()

# Use manual country code if set, otherwise use geolocalizaion
if country_code:
    # Retrieve data from Co2Signal API
    co2data = api_calls.get_request_co2signal(countrycode=country_code)
else:
    # Get location
    geolocation = api_calls.get_location()
    lon = geolocation['longitude']
    lat = geolocation['latitude']
    # Retrieve data from Co2Signal API
    co2data = api_calls.get_request_co2signal(lon, lat)

print('\nRetrieving Co2Signal data...')
# Extract relevant measures
carbon_intensity = co2data['data']['carbonIntensity']
carbon_intensity_unit = co2data['units']['carbonIntensity']
fossil_percentage = round(co2data['data']['fossilFuelPercentage'],2)
print("- Selected Country: {0} \n- Carbon Intensity: {1} ({2}) \n- Percentage of fossil fuel: {3}%".format(country_code, carbon_intensity, carbon_intensity_unit, fossil_percentage))

# Retrieve cpu info
print('\nRetrieving CPU data...')
cpu_info = em.get_cpu_info()
cpu_usage = em.get_cpu_usage(10) #it seems too low to be true!
print("- Current CPU: {0} \n- CPU usage during last 10s: {1}%".format(cpu_info, cpu_usage))
