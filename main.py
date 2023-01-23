import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import exceptions


# Define url of interest (Italy)
url_electricity_map = "https://app.electricitymaps.com/zone/IT?aggregated=true"

def browser_setup(browser_name):
    '''Inizialize webdriver paramiters for a specific browser

    Parameters
    ----------
    browser_name: string
        Name of the browser, either 'Chrome' or 'Firefox'.

    Returns
    -------
    driver: selenium.webdriver
        webdriver object with paramenters for the chosen browser.

    '''
    if browser_name == 'Chrome':
        # Set driver of Chrome (requires version > 9.0)
        options = webdriver.ChromeOptions()
        # Disable popup
        options.add_argument("--headless")
        options.add_argument("--window-size=%s" % WINDOW_SIZE)
        driver = webdriver.Chrome(options=options)
    elif browser_name == 'Firefox':
        # Set driver for Firefox
        options = webdriver.FirefoxOptions()
        #Disable popup
        options.add_argument("--headless")
        options.add_argument("--window-size=%s" % WINDOW_SIZE)
        driver = webdriver.Firefox(options=options)

    return driver


# Try with Chrome, if fails try with Firefox
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
    print('Google Chrome or Firefox not found, plese install either of them')
