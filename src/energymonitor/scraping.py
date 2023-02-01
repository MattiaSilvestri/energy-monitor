from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

def chrome_browser_setup():
    """
    Inizialize webdriver paramiters for a specific browser

    :return: Webdriver object with paramenters for the chosen browser.
    :rtype: selenium.webdriver
    """

    # Set driver of Chrome (requires version > 9.0)
    options = webdriver.ChromeOptions()
    # Specify verbosity level 0:info, 1:warnings, 2:error, 3:fatal
    options.add_argument('log-level=1')    
    # Disable popup
    options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    return driver


def get_carbon_intensity(html):
    """
    Get the carbon intensity value of a certain country from the left panel of Electricity Map

    :param html: The html content requested with selenium
    :type html: str
    :return: The value representing the current carbon intensity for a given country
    :rtype: str
    """

    soup = BeautifulSoup(html, "html.parser")
    carbon_intensity_square = soup.find_all("p", attrs={"data-test-id": "co2-square-value"})
    carbon_intensity_value = carbon_intensity_square[0].text
    return carbon_intensity_value
        