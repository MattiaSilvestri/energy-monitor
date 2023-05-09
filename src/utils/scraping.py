from bs4 import BeautifulSoup
import json
import os
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager # type: ignore


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


def scrape_tdp_intel(cpu_name) -> float:
    """
    Retrieve the TDP of the CPU from the Intel website.

    :param cpu_name: CPU name, coming from get_cpu_info()
    :return: CPU Thermal Design Power (TDP) in watts
    """
    # initialize the webdriver
    driver = chrome_browser_setup()
    # open the intel website with selenium
    search_url = "https://ark.intel.com/content/www/us/en/ark/search.html?_charset_=UTF-8&q="
    driver.get(search_url)
    # get the search bar
    search_bar = driver.find_element(By.ID, "ark-searchbox")
    # send the cpu_name to the search bar on the website
    search_bar.send_keys([x for x in cpu_name.split(' ') if x.startswith('i')][0])
    # search for the name that was sent
    search_bar.send_keys(Keys.RETURN)
    # find the span element that contains the TDP, identified by the attribute "MaxTDP"
    tdp = driver.find_element(By.XPATH, "//span[@data-key='MaxTDP']").text
    # retain only the numbers including the decimal points, if present
    tdp = float(re.findall(r'\d+\.\d+|\d+', tdp)[0])
    # close the driver
    driver.close()
    # return the tdp
    return tdp


def get_AMD_database(fname) -> dict:
    """
    retieve the AMD database from out github repository

    :param fname: name of the json file to be saved
    :return: dictionary containing the AMD database
    """
    # url of the json file in our github repository
    # todo: update according to branch 
    url = 'https://raw.githubusercontent.com/MattiaSilvestri/energy-monitor/cpu_data/data/tableExport.json'
    # get the json file in the url using requests and parse it as json format
    data = requests.get(url).json()
    # save it in the data folder
    with open(fname, 'w') as f:
        json.dump(data, f)
    return data