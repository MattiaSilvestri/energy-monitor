from utils import api_calls, cpu
from PyQt5.QtWidgets import QApplication
import sys
from core.gui import PlotWindowApp

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
        print('\nRetrieving CPU data...')
        cpu_retrieval_time = 1 # TODO: add to config
        cpu_info = cpu.get_cpu_info()
        print("- Current CPU: {0}".format(cpu_info))

        # Launch plot
        app = QApplication(sys.argv)
        app.setStyleSheet('''
            QWidget {
                font-size: 30px;
            }
        ''') # TODO: add to config
        myApp = PlotWindowApp(cpu.get_cpu_tdp(cpu_info), carbon_intensity, cpu_retrieval_time, get_interval_emissions, 
                              num_x_points=200, num_x_ticks=5, x_unit_measurement="m", y_unit_measurement="h") # TODO: add to config
        myApp.show()
        print('\nPlot window in execution...')
        try:
            sys.exit(app.exec_())
        except SystemExit:
            print('Closing Window and Saving Results...')
            myApp.save_log()

    except KeyError:
        print('Sorry, your country is not present in the Electricity Map ' +
              'database, it is therefore not possible to retrieve CO2 emissions data.')


def combine_cpu_CO2(cpu_usage: float, usage_time: int, cpu_tdp: int, co2_intensity: float) -> float:
    """
    Combine CPU usage, CPU TDP and CO2 intensity to compute CO2 consumption.

    :param cpu_usage: average CPU usage over a time interval period
    :type cpu_usage: float
    :param usage_time: CPU usage time period in seconds
    :type usage_time: int
    :param cpu_tdp: CPU Thermal Design Power (TDP) in watts
    :type cpu_tdp: int
    :param co2_intensity: carbon intensity value for the selected country
    :type co2_intensity: float
    :return: grams of CO2 emitted for your CPU usage in the specified time
    :rtype: float
    """
    # transfrom Watt in kWatt
    cpu_tdp_KW = cpu_tdp/1000

    # transfrom kW in kWh and take a certain proportion of it
    used_KWh = cpu_usage * cpu_tdp_KW / 100 * (usage_time/3600)

    # get the g of Co2
    co2_emissions = round(used_KWh * co2_intensity, 6) # TODO: add to config

    return co2_emissions


def get_interval_emissions(cpu_tdp: int, co2_intensity: float, time_frequency: int) -> float:
    """
    From a given cpu_tdp and co2_intensity return the co2 emissions computing the cpu_usage at current time.

    :param cpu_tdp: CPU Thermal Design Power (TDP) in watts
    :type cpu_tdp: int
    :param co2_intensity: carbon intensity value for the selected country
    :type co2_intensity: float
    :param time_frequency: frequency of CPU usage estimation in seconds
    :type time_frequency: int
    :return: grams of CO2 emitted for your CPU usage in the specified time
    :rtype: float
    """

    # Retrieve cpu usage
    cpu_usage = cpu.get_cpu_usage(time_frequency-0.05) # TODO: add to config

    # Combine Co2 with CPU usage
    co2_emissions = combine_cpu_CO2(cpu_usage, time_frequency, cpu_tdp, co2_intensity)

    return co2_emissions