from bs4 import BeautifulSoup
import numpy as np
import json
import os
import re
import requests
import time


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


def get_cpu_database(fname, cpu_brand) -> dict:
    """
    retieve the database (either intel or amd) from out github repository

    :param fname: name of the json file to be saved
    :return: dictionary containing the AMD database
    """
    # url of the json file in our github repository
    # todo: update according to branch 
    url = f'https://raw.githubusercontent.com/MattiaSilvestri/energy-monitor/main/data/database_{cpu_brand}.json'
    # get the json file in the url using requests and parse it as json format
    data = requests.get(url).json()
    # save it in the data folder
    with open(fname, 'w') as f:
        json.dump(data, f)

    return data


def _create_intel_database():
    """
    Create the database of Intel CPUs and their TDPs, scraping information from the intel website.

    """
    def _isintel(tag):
        return tag.has_attr('data-value') and 'Intel' in tag['data-value']
    
    # initialize the dictionary
    intel_database = dict()

    # get the list of processors families from the intel website
    search_url = "https://www.intel.com/content/www/us/en/products/details/processors.html"
    soup = BeautifulSoup(requests.get(search_url).content, 'html.parser')
    # find the title class
    group_list = soup.find_all("div", attrs={"class": "group-title has-name"})
    # iterate over processor groups
    for group in group_list:
        # get href, insert 'products' before .html and transform href to url
        group_url = 'https://www.intel.com' + group.find("a")['href'].replace('.html', '/products.html')
        soup = BeautifulSoup(requests.get(group_url).content, 'html.parser')
        # stop the loop for a random time between 0 and 1 seconds to avoid being blocked
        time.sleep(np.random.rand())
        # isolate the list of processors by looking for the data-value that contains 'Intel'
        processor_list = soup.find_all(_isintel)
        # if it is empty, skip
        if not processor_list:
            continue
        # iterate over processors
        for processor in processor_list:
            # get href and transform to url
            processor_url = 'https://www.intel.com' +  processor.find("a")['href']
            # request the processor page
            soup = BeautifulSoup(requests.get(processor_url).content, 'html.parser')
            # stop the loop for a random time between 0 and 1 seconds to avoid being blocked
            time.sleep(np.random.rand())
            # get the tdp
            processor_specs = soup.find_all("div", attrs={"class": "row tech-section-row"})
            # iterate over specs
            for spec in processor_specs:
                # check if tech-label contains 'TDP'
                if spec.find("div", attrs={"class": "tech-label"}) is not None:
                    if 'TDP' in spec.find("div", attrs={"class": "tech-label"}).text:
                        # get the tdp
                        tdp = spec.find("div", attrs={"class": "tech-data"}).text
                        # retain only the numbers including the decimal points, if present
                        tdp = float(re.findall(r'\d+\.\d+|\d+', tdp)[0])
                        # store in dictionary
                        intel_database[processor['data-value']] = tdp
                        # break the loop over specs, to speed up the process
                        break
    # save the dictionary in a json file
    # get the path to the data folder
    path = [x[0] for x in os.walk('..') if 'data' in x[0]][0]
    fname = os.path.join(path, 'database_intel.json')
    with open(fname, 'w') as f:
        json.dump(intel_database, f)
