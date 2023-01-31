import time
from bs4 import BeautifulSoup
from selenium.common import exceptions
from energymonitor import browser_setup

# Define url of interest (Italy)
url_electricity_map = "https://app.electricitymaps.com/zone/IT?aggregated=true"

# Try with Chrome, if it fails try with Firefox
for b in ['Chrome', 'Firefox']:
    no_browser = False
    try:
        print('Trying acces with ', b)
        driver = browser_setup(b)
        driver.get(url_electricity_map)
        time.sleep(3) #give time for dynamic text to load
        html = driver.page_source
        driver.quit()
        # Find carbon intensity data on left panel
        soup = BeautifulSoup(html, "html.parser")
        carbon_intensity_square = soup.find_all("p", attrs={"data-test-id": "co2-square-value"})
        carbon_intensity_value = carbon_intensity_square[0].text
        print("Italy Carbon Intensity: {0} (gCO₂eq/kWh)".format(carbon_intensity_value))
    except exceptions.WebDriverException:
        no_browser = True
        continue
    else:
        break

if no_browser == True:
    print('Google Chrome or Firefox not found, please install either of them')
