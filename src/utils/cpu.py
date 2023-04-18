import cpuinfo
import json
import os
import pandas as pd
import psutil
import re
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
    Get the CPU Thermal Design Power (TDP) in watts from the manufacturer.

    :return: CPU Thermal Design Power (TDP) in watts
    :rtype: int
    """
    json_fname = os.path.join('..', 'data', 'cpu_tdp.json')
    if os.path.exists(json_fname):
        # load json file with the cpu tdp info
        with open(json_fname, 'r') as f:
            tdp = json.load(f)['tdp']
    else: 
        # get the cpu name
        cpu_name = get_cpu_info()
        if 'Intel' in cpu_name:
            # retrieve information from the intel website
            # initialize the driver
            from utils.scraping import chrome_browser_setup
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
        elif 'AMD' in cpu_name:
            # use the json file stored in the data folder to retrieve the TDP
            # Opening JSON file
            f = open(os.path.join('..', 'data', 'tableExport.json'))
            # returns JSON object as a dictionary
            data = json.load(f)
            # Iterate through the json to get the model name and the TDP
            for model_info in data['data']:
                # remove non alphanumeric characters (i.e., TM) from Model name
                model = re.sub(r'\W+', ' ', model_info['Model'])
                if model in cpu_name:
                    # get the TDP, remove the non numeric characters and convert to float
                    tdp = float(re.sub(r'\D+', '', model_info['Default TDP']))
                    break
        else:
            raise ValueError('CPU not supported')
        # save the tdp in a json file
        with open(json_fname, 'w') as f:
            json.dump({'tdp': tdp}, f)
    # return the tdp value
    return tdp
        
