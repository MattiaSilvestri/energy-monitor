from core.cpuCO2 import cpu_co2
from utils import cli

# Script for launching the app

args = cli.get_args()

if args.list:
    # Display country list if requested
    country_code = cli.show_list()
    cpu_co2(country_code=country_code)
elif args.country:
    # Launch main with manual country selection
    country_code = args.country
    cpu_co2(country_code=country_code)
else:
    # Disclaimer message
    print("The application uses IP geolocation to retrieve your position. If you \
want to disable automatic geolocation, launch the application with the the --set-country flag to \
manually input your country. Unfortunately the Electricity Map database doesn't \
contain all countries, so your country might not have CO2 data even if it's \
present in the list.", end="\n")

    # Get confirmation from user
    while True:
        confirm = input("Continute with geolocation? [y/n] ")

        if confirm == "y" or confirm == "yes":
            # Launch main with geolocalizaion
            cpu_co2()
            break
        elif confirm == "n" or confirm == "no":
            country_code = cli.show_list()
            cpu_co2(country_code=country_code)
            break
        else:
            print("Please reply with either yes (y) or no (n).\n")
