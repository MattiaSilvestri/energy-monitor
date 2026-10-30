import cpuinfo  # type: ignore
import json
import psutil
import re
import sys

from energy_monitor.utils.paths import (
    bundled_cpu_database,
    cpu_database_file,
    load_user_data,
    update_user_data,
)
from energy_monitor.utils.scraping import get_cpu_database


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
    # load the cached cpu tdp info, if any
    user_data = load_user_data()
    if "tdp" in user_data and not "pytest" in sys.modules:
        tdp = user_data["tdp"]
    else:
        # get the brand of the CPU of this computer
        cpu_brand = "intel" if "Intel" in cpu_name else "amd"
        # use the database downloaded by the user, then the one shipped with the package
        database_fname = cpu_database_file(cpu_brand)
        bundled_fname = bundled_cpu_database(cpu_brand)
        if database_fname.is_file():
            with open(database_fname, "r") as f:
                data = json.load(f)
        elif bundled_fname.is_file():
            with bundled_fname.open("r") as f:
                data = json.load(f)
        else:
            # download it from our github repository
            data = get_cpu_database(database_fname, cpu_brand)
        # retrieve the model code (identified by digits and alphabetic character) from cpu_name
        my_model_code = re.findall(r"\d+\w+", cpu_name)[0]
        # initialize the list of TDPs. this is to account for multiple potential matches
        tdp = []
        if cpu_brand == "amd":
            # Iterate through the json to get the model name and the TDP
            for model_info in data["data"]:
                # retrieve the model code (identified by digits and alphabetic character) from cpu_name
                this_model_code = re.findall(r"\d+\w+", str(model_info["Model"]))[0]
                # check that the model code of this iteration matches the one of the CPU of the user
                if this_model_code == my_model_code:
                    # get the TDP of the CPU
                    model_tdp = model_info["Default TDP"]
                    # check if its empty
                    if model_tdp == "":
                        # e.g., model_info['Model'] = AMD Ryzen 7 7736U
                        raise ValueError(
                            f"TDP not found for model {model_info['Model']}"
                        )
                    # split model tdp string by any non-numeric character, remove empty strings and convert to float
                    model_tdp = [
                        float(x)
                        for x in list(filter(None, re.split(r"\D+", model_tdp)))
                    ]
                    if len(model_tdp) > 1:
                        # average the TDPs
                        tdp.append(sum(model_tdp) / len(model_tdp))
                    else:
                        tdp.append(model_tdp[0])
        elif cpu_brand == "intel":
            for model_name, model_tdp in data.items():
                if my_model_code in model_name:
                    tdp.append(model_tdp)
        else:
            raise ValueError("CPU not supported")

        tdp = list(set(tdp))
        if not tdp:
            raise ValueError(f"TDP not found in the database for CPU '{cpu_name}'")
        if len(tdp) > 1:
            raise ValueError(f"Found multiple matching TDPs for CPU '{cpu_name}': {tdp}")
        tdp = tdp[0]
    # save the tdp in the user data file
    update_user_data(tdp=tdp)
    # return the tdp value
    return float(tdp)
