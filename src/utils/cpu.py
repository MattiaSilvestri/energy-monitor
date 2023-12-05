import cpuinfo # type: ignore
import json
import os
import psutil
import re
import sys
from utils.scraping import get_cpu_database


def get_cpu_info() -> str:
    """
    Return info regarding CPU model installed.
    :return: Info regarding CPU model installed
    :rtype: str
    """
    try:
        cpu_info = cpuinfo.get_cpu_info()["brand_raw"]
    except Exception as e:
        print("Error retrieving CPU info. Stopping execution.")
        sys.exit(1)
                
    return cpu_info


def get_cpu_usage(seconds: float) -> float:
    """
    Return the average CPU usage over a time interval period.

    :param seconds: Time interval period considered
    :type seconds: float
    :return: CPU usage percentage
    :rtype: float 
    """
    cpu_percentage = psutil.cpu_percent(seconds)
        
    return cpu_percentage


def get_cpu_tdp(cpu_name: str) -> float:
    """
    Get the CPU Thermal Design Power (TDP) in watts from the manufacturer.

    :param cpu_name: CPU name, coming from get_cpu_info()
    :return: CPU Thermal Design Power (TDP) in watts
    :rtype: float
    """
    # get the path to the data folder
    path = os.path.join(os.path.dirname(__file__).split("energy-monitor")[0], 'energy-monitor', 'data')
    # define file name of the output file
    json_fname = os.path.join(path, 'cpu_tdp.json')
    if os.path.isfile(json_fname) and not 'pytest' in sys.modules:
        # load json file with the cpu tdp info
        with open(json_fname, 'r') as f:
            tdp = json.load(f)['tdp']
    else: 
        # get the brand of the CPU of this computer
        cpu_brand = 'intel' if 'Intel' in cpu_name else 'amd'            
        # use the json file stored in the data folder to retrieve the TDP
        database_fname = os.path.join(path, f'database_{cpu_brand}.json')
        print(database_fname)
        if not os.path.isfile(database_fname):
            # download it from our github repository
            data = get_cpu_database(database_fname, cpu_brand)
        else:
            # returns JSON object as a dictionary
            data = json.load(open(database_fname))
        # retrieve the model code (identified by digits and alphabetic character) from cpu_name
        my_model_code = re.findall(r'\d+\w+', cpu_name)[0]
        # initialize the list of TDPs. this is to account for multiple potential matches
        tdp = []
        if cpu_brand == 'amd':
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
        elif cpu_brand == 'intel':
            for model_name, model_tdp in data.items():
                if my_model_code in model_name:     
                    tdp.append(model_tdp)
        else:
            raise ValueError('CPU not supported')
        
        assert len(tdp) == 1, 'Found multiple matching TDPs'
        tdp = tdp[0]
    # save the tdp in a json file
    with open(json_fname, 'w') as f:
        json.dump({'tdp': tdp}, f)
    # return the tdp value
    return float(tdp)
