#!/usr/bin/env python3

import argparse
import requests
from InquirerPy import inquirer
from InquirerPy import get_style
from itertools import repeat
import shutil
import os
import sys
import json

help_message = "It collects CO2 emissions data from your country and compare \
it with your energy consumption to produce an estimate of the CO2 generated \
by your computer."
parser = argparse.ArgumentParser(description=help_message)


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
        help="Generate copy of default config in the specified folder",
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

    # Get path to project directory
    path = os.path.dirname(__file__).split("energy_monitor")[0]
    # Define the source path of the config files within your package
    source_path = os.path.join(path, "energy_monitor", "config", "config.yml")

    # Copy or move the config files
    try:
        shutil.copyfile(source_path, destination_path)
        print("Config files have been installed successfully.")
    except Exception as e:
        print(f"An error occurred while installing config files: {e}")

    # Write user path in json file
    data_path = os.path.join(path, "energy_monitor", "data")
    # define file name of the output file
    json_fname = os.path.join(data_path, "user_data.json")
    if os.path.isfile(json_fname) and not "pytest" in sys.modules:
        # load json file with the cpu tdp info
        with open(json_fname, "r") as f:
            user_data = json.load(f)

        user_data["user_config"] = destination_path

        with open(json_fname, "w") as f:
            json.dump(user_data, f)
