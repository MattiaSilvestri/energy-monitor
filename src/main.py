import energymonitor

# Define zone of interest
country_code = "IT"


# Retrieve data from Co2Signal API
print('Retrieving Co2Signal data...')
co2data = energymonitor.get_request_co2signal(country_code)

# Extract relevant measures
carbon_intensity = co2data['data']['carbonIntensity']
carbon_intensity_unit = co2data['units']['carbonIntensity']
fossil_percentage = co2data['data']['fossilFuelPercentage']
print("\n Selected Country: {0} \n Carbon Intensity: {1} ({2}) \n Percentage of fossil fuel: {3}%".format(country_code, carbon_intensity, carbon_intensity_unit, fossil_percentage))

# Retrieve cpu info
print('Retrieving CPU data...')
cpu_info = energymonitor.get_cpu_info()
print("\n Current CPU: {0}".format(cpu_info))