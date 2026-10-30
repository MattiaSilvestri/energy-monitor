#!/usr/bin/env python3

import argparse
import requests
from InquirerPy import inquirer
from InquirerPy import get_style
from itertools import repeat
import shutil
import os
import sys
from typing import List
from urllib.parse import quote_plus

from energy_monitor.utils.api_calls import save_api_keys
from energy_monitor.utils.paths import DEFAULT_CONFIG, secrets_file, update_user_data

help_message = "It collects CO2 emissions data from your country and compare \
it with your energy consumption to produce an estimate of the CO2 generated \
by your computer."
parser = argparse.ArgumentParser(description=help_message)


def positive_float(value: str) -> float:
    try:
        number = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a number")
    if number <= 0:
        raise argparse.ArgumentTypeError("the value must be greater than 0")
    return number


def get_args() -> argparse.Namespace:
    """
    Collects command line arguments from user.

    :return: Namespace object containing the option selected by the user
    :rtype: arparse.Namespace
    """

    parser.add_argument(
        "-c", "--set-country", dest="country", type=str, help="Manually set location"
    )
    parser.add_argument(
        "-l",
        "--show-list",
        dest="list",
        action="store_true",
        help="Show list of available country codes",
    )
    parser.add_argument(
        "-C",
        "--install-config",
        dest="filename",
        type=str,
        help="Generate copy of default config at the specified path and use it",
    )
    parser.add_argument(
        "-k",
        "--set-api-keys",
        dest="set_keys",
        action="store_true",
        help="Store the Electricity Maps and ipgeolocation API keys",
    )
    parser.add_argument(
        "-t",
        "--set-tdp",
        dest="tdp",
        type=positive_float,
        metavar="WATTS",
        help="Manually set the TDP of your CPU in watts",
    )
    args = parser.parse_args()
    return args


def show_list() -> str:
    """
    Display a searchable list of available countries and their code in
    alphabetical order and returns the ID of the selected country.

    :return: ID of the selected country
    :rtype: str
    """

    url = "https://api.electricitymap.org/v3/zones"
    # Perform the API call
    req = requests.get(url)

    # Display country list
    country_map = {}
    for k in req.json():
        zone = req.json()[k]["zoneName"]
        country_map[zone] = k

    # Add searchable menu
    entries = list(repeat(0, len(country_map)))
    count = 0
    sorted_countries = {}
    for k in sorted(country_map):
        sorted_countries[k] = country_map[k]
        entries[count] = k + " : " + sorted_countries[k]
        count += 1

    style = get_style({"fuzzy_prompt": "hidden"}, style_override=False)

    confirm = False
    while not confirm:
        select = inquirer.fuzzy(
            message="Select country (start typing to search):",
            choices=entries,
            vi_mode=True,
            border=True,
            amark="",
            qmark="",
            pointer="> ",
            style=style,
            keybindings={
                "interrupt": [{"key": "c-c"}],
                "down": [{"key": "c-j"}, {"key": "down"}],
                "up": [{"key": "c-k"}, {"key": "up"}],
            },
        ).execute()
        confirm = inquirer.confirm(
            message="Confirm?", amark="", qmark="", default=True
        ).execute()

    # Get ID of the selected country
    country_id = select.split()[-1]

    return country_id


def install_config(destination_path) -> None:
    """
    Install config file if not present.
    """

    destination_path = os.path.abspath(os.path.expanduser(destination_path))
    if os.path.isdir(destination_path):
        destination_path = os.path.join(destination_path, "config.yml")

    # Copy the default config shipped with the package
    try:
        with DEFAULT_CONFIG.open("rb") as src, open(destination_path, "wb") as dst:
            shutil.copyfileobj(src, dst)
        print(f"Config file has been installed successfully in {destination_path}")
    except Exception as e:
        print(f"An error occurred while installing config files: {e}")
        return

    # Remember the user config path
    if not "pytest" in sys.modules:
        update_user_data(user_config=destination_path)


def ask_cpu_tdp(cpu_name: str, reason: str, candidates: List[float]) -> float:
    """
    Ask the user for the TDP of their CPU, when it cannot be found in the database.

    :param cpu_name: CPU name, coming from get_cpu_info()
    :param reason: why the TDP could not be found automatically
    :param candidates: possible TDP values found in the database, if any
    :return: CPU Thermal Design Power (TDP) in watts
    :rtype: float
    """
    print(
        f"\n{reason}.\n"
        "The TDP (Thermal Design Power) is listed in the CPU specifications on the "
        "manufacturer website, for example:\n"
        f"https://duckduckgo.com/?q={quote_plus(cpu_name + ' TDP')}\n"
        "It will be saved, you can change it later with 'energy-monitor --set-tdp WATTS'."
    )

    manual = "Type it manually"
    if candidates:
        choice = inquirer.select(
            message="Select the TDP of your CPU:",
            choices=[f"{c:g} W" for c in candidates] + [manual],
        ).execute()
        if choice != manual:
            return float(choice.split()[0])

    tdp = inquirer.text(
        message="TDP of your CPU in watts:",
        validate=lambda v: _is_positive_float(v),
        invalid_message="Please type a number greater than 0 (e.g. 15)",
    ).execute()
    return float(tdp)


def _is_positive_float(value: str) -> bool:
    try:
        return float(value) > 0
    except ValueError:
        return False


def set_tdp(tdp: float) -> None:
    """
    Save the TDP of the CPU set manually by the user.
    """
    update_user_data(tdp=tdp)
    print(f"CPU TDP set to {tdp:g} W")


def set_api_keys() -> None:
    """
    Ask the user for the API keys and store them in the user secrets file.
    """
    print(
        "Get your free API keys at:\n"
        "- Electricity Maps: https://portal.electricitymaps.com/\n"
        "- ipgeolocation:    https://ipgeolocation.io/\n"
        "Leave a field empty to keep the current value."
    )
    keys = {
        "co2signal": inquirer.secret(message="Electricity Maps API key:").execute(),
        "ipgeolocation": inquirer.secret(message="ipgeolocation API key:").execute(),
    }
    save_api_keys({k: v.strip() for k, v in keys.items()})
    print(f"API keys saved in {secrets_file()}")
