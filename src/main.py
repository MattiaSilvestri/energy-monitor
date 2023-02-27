import energymonitor as em
from energymonitor import api_calls
from energymonitor import cli

def main(args) -> None:

    country_code = args.country
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


args = cli.get_args()

if args.list:
    # Display country list if requested
    cli.show_list()
elif args.country:
    # Launch main with manual country selection
    country_code = args.country
    main(country_code)
else:
    # Disclaimer message
    print("The application uses IP geolocation to retrieve your position. If you \
want to disable automatic geolocation, launch the application with the the --set-country flag to \
manually input your country.", end="\n")

    # Get confirmation from user
    while True:
        confirm = input("Continute with geolocation? [y/n] ")

        if confirm == "y" or confirm == "yes":
            # Launch main with geolocalizaion
            main(args)
            break
        elif confirm == "n" or confirm == "no":
            country_code = input("Insert conutry code: ")
            main(country_code)
            break
        else:
            print("Please reply with either yes (y) or no (n).\n")
