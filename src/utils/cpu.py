import cpuinfo
import os
import pandas as pd
import psutil
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def get_cpu_info():
    """
    Return info regarding CPU model installed.

    :return: Info regarding CPU model installed
    :rtype: str
    """

    try:
        cpu_info = cpuinfo.get_cpu_info()["brand_raw"]
    except:
        cpu_info= "CPU Info not available"
        
    return cpu_info


def get_cpu_usage(seconds):
    """
    Return the average CPU usage over a time interval period.

    :param seconds: Time interval period considered
    :type seconds: float
    :return: CPU usage percentage
    :rtype: float or None
    """

    try:
        cpu_percentage = psutil.cpu_percent(seconds)
    except:
        cpu_percentage= None
        
    return cpu_percentage

def get_cpu_tdp():
    """
    Mock function to be replaced soon.

    :return: CPU Thermal Design Power (TDP) in watts
    :rtype: int
    """
    if os.path.exists(os.path.join('../data', 'cpu_tdp.csv')):
        return pd.read_csv(os.path.join('../data', 'cpu_tdp.csv'))
    else: # retrieve data from web
        # get the cpu name
        cpu_name = get_cpu_info()
        # cpu_name = 'Intel(R) Core(TM) i7-10510U CPU @ 1.80GHz'
        if 'Intel' in cpu_name:
            from utils.scraping import chrome_browser_setup
            driver = chrome_browser_setup()
            # open the intel website with selenium
            search_url = "https://ark.intel.com/content/www/us/en/ark/search.html?_charset_=UTF-8&q="
            driver.get(search_url)
            # search bar is identified by
            # <input type="search" id="ark-searchbox" name="q" class="support-searchbox ui-autocomplete-input" placeholder="Search specifications">
            search_bar = driver.find_element(By.ID, "ark-searchbox")
            # send the cpu_name to the search bar on the website
            search_bar.send_keys([x for x in cpu_name.split(' ') if x.startswith('i')][0])
            # search for the name that was sent
            search_bar.send_keys(Keys.RETURN)
            driver.save_screenshot('/Users/giulianogiari/Desktop/test.png')

            specs_list = driver.find_element(By.CLASS_NAME, "specs-list")
            # todo: get the TDP from the specs list
    
