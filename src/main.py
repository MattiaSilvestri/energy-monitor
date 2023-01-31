import time
from selenium.common import exceptions
import energymonitor

# Define url of interest (Italy)
url_electricity_map = "https://app.electricitymaps.com/zone/IT?aggregated=true"

# Try with Chrome, if it fails try with Firefox
for b in ['Chrome', 'Firefox']:
    no_browser = False
    try:
        print('Trying acces with ', b)
        driver = energymonitor.browser_setup(b)
        driver.get(url_electricity_map)
        time.sleep(3) #give time for dynamic text to load
        html = driver.page_source
        driver.quit()
        # Find carbon intensity data on left panel
        carbon_intensity_value = energymonitor.get_carbon_intensity(html)
        print("Italy Carbon Intensity: {0} (gCO₂eq/kWh)".format(carbon_intensity_value))
        print(type(html))
    except exceptions.WebDriverException:
        no_browser = True
        continue
    else:
        break

if no_browser == True:
    print('Google Chrome or Firefox not found, please install either of them')