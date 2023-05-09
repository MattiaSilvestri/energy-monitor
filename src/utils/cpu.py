import cpuinfo
import json
import os
import psutil
import re
import warnings
from utils.scraping import scrape_tdp_intel, get_AMD_database


def get_cpu_info() -> str:
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



def get_cpu_usage(seconds: float) -> float or None:
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


def get_cpu_tdp(cpu_name: str) -> float:
    """
    Get the CPU Thermal Design Power (TDP) in watts from the manufacturer.

    :param cpu_name: CPU name, coming from get_cpu_info()
    :return: CPU Thermal Design Power (TDP) in watts
    :rtype: float
    """
    json_fname = os.path.join('..', 'data', 'cpu_tdp.json')
    if os.path.isfile(json_fname):
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
            # retrieve the model code (identified by digits and alphabetic character) from cpu_name
            my_model_code = re.findall(r'\d+\w+', cpu_name)[0]
            # initialize the list of TDPs. this is to account for multiple potential matches
            tdp = []
            # Iterate through the json to get the model name and the TDP
            for model_info in data['data']:
                # retrieve the model code (identified by digits and alphabetic character) from cpu_name
                this_model_code = re.findall(r'\d+\w+', str(model_info['Model']))[0]
                # check that the model code of this iteration matches the one of the CPU of the user
                if this_model_code == my_model_code:
                    # get the TDP of the CPU
                    model_tdp = model_info['Default TDP']
                    # check if its empty
                    if model_tdp == '':
                        # e.g., model_info['Model'] = AMD Ryzen 7 7736U
                        raise ValueError(f"TDP not found for model {model_info['Model']}")
                    # split model tdp string by any non-numeric character, remove empty strings and convert to float
                    model_tdp =  [float(x) for x in list(filter(None, re.split(r'\D+', model_tdp)))]
                    if len(model_tdp) > 1:
                        # average the TDPs
                        tdp.append(sum(model_tdp) / len(model_tdp))
                    else:
                        tdp.append(model_tdp[0])
            assert len(tdp) == 1, 'Found multiple matching TDPs'
            tdp = tdp[0]
        else:
            raise ValueError('CPU not supported')
        # save the tdp in a json file
        with open(json_fname, 'w') as f:
            json.dump({'tdp': tdp}, f)
    # return the tdp value
    return tdp
