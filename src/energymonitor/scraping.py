from bs4 import BeautifulSoup
from selenium import webdriver

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
        driver = webdriver.Chrome(options=options)
    elif browser_name == 'Firefox':
        # Set driver for Firefox
        options = webdriver.FirefoxOptions()
        #Disable popup
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)

    return driver

def get_carbon_intensity(html):
    '''
    Get the carbon intensity value of a certain country from the left panel of Electricity Map

    :param html: The html content requested with selenium
    :type html: str
    :return: The value representing the current carbon intensity for a given country
    :rtype: str
    '''
    soup = BeautifulSoup(html, "html.parser")
    carbon_intensity_square = soup.find_all("p", attrs={"data-test-id": "co2-square-value"})
    carbon_intensity_value = carbon_intensity_square[0].text
    return carbon_intensity_value
        