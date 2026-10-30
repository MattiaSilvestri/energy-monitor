import cpuinfo  # type: ignore
import json
import psutil
import re
import sys
from typing import List, Optional

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


class TDPNotFoundError(LookupError):
    """Raised when the TDP of a CPU cannot be determined from the database."""

    def __init__(self, message: str, candidates: Optional[List[float]] = None):
        super().__init__(message)
        self.candidates = candidates or []


def lookup_cpu_tdp(cpu_name: str) -> float:
    """
    Look up the CPU Thermal Design Power (TDP) in watts in the CPU database.

    :param cpu_name: CPU name, coming from get_cpu_info()
    :return: CPU Thermal Design Power (TDP) in watts
    :rtype: float
    :raises TDPNotFoundError: if the CPU is not in the database or matches multiple TDPs
    """
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
    model_codes = re.findall(r"\d+\w+", cpu_name)
    if not model_codes:
        raise TDPNotFoundError(f"Could not read the model code of CPU '{cpu_name}'")
    my_model_code = model_codes[0]
    # initialize the list of TDPs. this is to account for multiple potential matches
    tdp = []
    if cpu_brand == "amd":
        # Iterate through the json to get the model name and the TDP
        for model_info in data["data"]:
            # retrieve the model code (identified by digits and alphabetic character) from cpu_name
            this_model_codes = re.findall(r"\d+\w+", str(model_info["Model"]))
            # check that the model code of this iteration matches the one of the CPU of the user
            if this_model_codes and this_model_codes[0] == my_model_code:
                # get the TDP of the CPU
                model_tdp = model_info["Default TDP"]
                # check if its empty
                if model_tdp == "":
                    # e.g., model_info['Model'] = AMD Ryzen 7 7736U
                    raise TDPNotFoundError(
                        f"TDP not available in the database for model {model_info['Model']}"
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
    else:
        for model_name, model_tdp in data.items():
            if my_model_code in model_name:
                tdp.append(model_tdp)

    tdp = sorted(set(tdp))
    if not tdp:
        raise TDPNotFoundError(f"CPU '{cpu_name}' not found in the TDP database")
    if len(tdp) > 1:
        raise TDPNotFoundError(
            f"Found multiple matching TDPs for CPU '{cpu_name}'", candidates=tdp
        )
    return float(tdp[0])


def get_cpu_tdp(cpu_name: str) -> float:
    """
    Get the CPU Thermal Design Power (TDP) in watts. The value is looked up in
    the CPU database the first time and then saved in the user data file.
    If the CPU is not in the database, the user is asked to type it.

    :param cpu_name: CPU name, coming from get_cpu_info()
    :return: CPU Thermal Design Power (TDP) in watts
    :rtype: float
    """
    # load the saved cpu tdp info, if any
    user_data = load_user_data()
    if "tdp" in user_data and not "pytest" in sys.modules:
        return float(user_data["tdp"])

    try:
        tdp = lookup_cpu_tdp(cpu_name)
    except TDPNotFoundError as e:
        if not sys.stdin.isatty() or "pytest" in sys.modules:
            raise ValueError(
                f"{e}. Set it manually with 'energy-monitor --set-tdp WATTS'"
            ) from e
        # imported here to avoid loading the interactive prompt when not needed
        from energy_monitor.utils.cli import ask_cpu_tdp

        tdp = ask_cpu_tdp(cpu_name, str(e), e.candidates)

    # save the tdp in the user data file
    update_user_data(tdp=tdp)
    return tdp
