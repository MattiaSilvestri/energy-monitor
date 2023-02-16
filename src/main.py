import time
from selenium.common import exceptions
import energymonitor

# Define url of interest (BritalItaly)
url_electricity_map = "https://app.electricitymaps.com/zone/IT?aggregated=true"

# Try with Chrome if installed
no_browser = False
try:
    print('Connecting to Chrome...')
    driver = energymonitor.chrome_browser_setup()
    driver.get(url_electricity_map)
    time.sleep(3) #give time for dynamic text to load
    html = driver.page_source
    driver.quit()
    # Find carbon intensity data on left panel
    carbon_intensity_value = energymonitor.get_carbon_intensity(html)
    print("Italy Carbon Intensity: {0} (gCO₂eq/kWh)".format(carbon_intensity_value))
    print("Current CPU: {0}".format(energymonitor.get_cpu_info()))
except exceptions.WebDriverException:
    no_browser = True

if no_browser == True:
    print('Google Chrome is not correctly installed, please install or update it.')