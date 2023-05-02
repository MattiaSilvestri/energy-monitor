import cpuinfo
import json
import os
import pandas as pd
import psutil
import re
from scraping import scrape_tdp_intel, get_AMD_database


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


def get_cpu_tdp(cpu_name) -> float:
    """
    Get the CPU Thermal Design Power (TDP) in watts from the manufacturer.

    :param cpu_name: CPU name, coming from get_cpu_info()
    :return: CPU Thermal Design Power (TDP) in watts
    :rtype: int
    """
    json_fname = os.path.join('..', 'data', 'cpu_tdp.json')
    if os.path.exists(json_fname):
        # load json file with the cpu tdp info
        with open(json_fname, 'r') as f:
            tdp = json.load(f)['tdp']
    else: 
        if 'Intel' in cpu_name:
            # retrieve information from the intel website
            tdp = scrape_tdp_intel(cpu_name)
        elif 'AMD' in cpu_name:
            # use the json file stored in the data folder to retrieve the TDP
            amd_fname = os.path.join('..', 'data', 'tableExport.json')
            if not os.path.isfile(amd_fname):
                # download it from our github repository
                data = get_AMD_database(amd_fname)
            else:
                # returns JSON object as a dictionary
                data = json.load(open(amd_fname))
            # Iterate through the json to get the model name and the TDP
            for model_info in data['data']:
                # remove non alphanumeric characters (i.e., TM) from Model name
                model = re.sub(r'\W+', ' ', str(model_info['Model']))
                if model in cpu_name:
                    print(model)
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
