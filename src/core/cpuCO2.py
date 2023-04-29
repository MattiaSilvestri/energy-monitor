from utils import api_calls, cpu
from PyQt5.QtWidgets import QApplication
import sys
from core.gui import MyApp

def cpu_co2(country_code = None) -> None:
    """Function to run the core of the app: compare CPU usage with CO2 emissions"""

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
        country_code = co2data['countryCode']

    try:
        # Extract relevant measures
        print('\nRetrieving Co2Signal data...')
        carbon_intensity = co2data['data']['carbonIntensity']
        carbon_intensity_unit = co2data['units']['carbonIntensity']
        fossil_percentage = round(co2data['data']['fossilFuelPercentage'],2)
        print("- Selected Country: {0} \n- Carbon Intensity: {1} ({2}) \n- Percentage of fossil fuel: {3}%".format(country_code, carbon_intensity, carbon_intensity_unit, fossil_percentage))

        # Retrieve cpu info
        cpu_retrieval_time = 2 #to export in a configuration file
        print(f'\nRetrieving CPU usage of the next {cpu_retrieval_time} seconds...')
        cpu_info = cpu.get_cpu_info()
        cpu_usage = cpu.get_cpu_usage(cpu_retrieval_time) #it seems too low to be true!
        print("- Current CPU: {0} \n- CPU usage during last 10s: {1}%".format(cpu_info, cpu_usage))

        # Combine Co2 with CPU usage
        print('\nCombining Co2 and CPU data...')
        co2_emissions = combine_cpu_CO2(cpu_usage, cpu.get_cpu_tdp(), carbon_intensity)
        print("- In the last {0} seconds your CPU footprint was: {1} g".format(cpu_retrieval_time, co2_emissions))

        # Launch plot
        app = QApplication(sys.argv)
        app.setStyleSheet('''
            QWidget {
                font-size: 30px;
            }
        ''')
        myApp = MyApp(cpu.get_cpu_tdp(), carbon_intensity, get_interval_emissions)
        myApp.show()
        print('\nPlot window is execution...')
        try:
            sys.exit(app.exec_())
        except SystemExit:
            print('Closing Window...')


    except KeyError:
        print('Sorry, your country is not present in the Electricity Map ' +
              'database, it is therefore not possible to retrieve CO2 emissions data.')


def combine_cpu_CO2(cpu_usage: float, cpu_tdp: int, co2_intensity: float) -> float:
    """
    Combine CPU usage, CPU TDP and CO2 intensity to compute CO2 consumption.

    :param cpu_usage: average CPU usage over a time interval period
    :type cpu_usage: float
    :param cpu_tdp: CPU Thermal Design Power (TDP) in watts
    :type cpu_tdp: int
    :param co2_intensity: carbon intensity value for the selected country
    :type co2_intensity: float
    :return: grams of CO2 emitted for your CPU usage in the specified time
    :rtype: float
    """
    cpu_tdp_KWh = cpu_tdp/1000
    used_KWh = cpu_usage * cpu_tdp_KWh / 100
    co2_emissions = round(used_KWh * co2_intensity, 2)
    return co2_emissions


def get_interval_emissions(cpu_tdp: int, co2_intensity: float) -> float:
    """
    From a given cpu_tdp and co2_intensity return the co2 emissions computing the cpu_usage at current time.

    :param cpu_tdp: CPU Thermal Design Power (TDP) in watts
    :type cpu_tdp: int
    :param co2_intensity: carbon intensity value for the selected country
    :type co2_intensity: float
    :return: grams of CO2 emitted for your CPU usage in the specified time
    :rtype: float
    """

    # Retrieve cpu usage
    cpu_retrieval_time = 1 #to export in a configuration file
    cpu_usage = cpu.get_cpu_usage(cpu_retrieval_time)

    # Combine Co2 with CPU usage
    co2_emissions = combine_cpu_CO2(cpu_usage, cpu_tdp, co2_intensity)

    return co2_emissions