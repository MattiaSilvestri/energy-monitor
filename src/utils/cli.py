#!/usr/bin/env python3

import argparse
import requests
from simple_term_menu import TerminalMenu
from itertools import repeat

help_message = 'It collects CO2 emissions data from your country and compare \
it with your energy consumption to produce an estimate of the CO2 generated \
by your computer.'
parser = argparse.ArgumentParser(description=help_message)

def get_args() -> argparse.Namespace:
    """
    Collects command line arguments from user.

    :return: Namespace object containing the option selected by the user
    :rtype: arparse.Namespace
    """

    parser.add_argument('-s', '--set-country', dest='country', type=str,
                        help='Manually set location')
    parser.add_argument('-l', '--show-list', dest='list', action='store_true',
                        help='Show list of available country codes')

    args = parser.parse_args()
    return args


def show_list() -> None:
    """
    Display list of available countries and their code in alphabetical order.

    :return: None
    :rtype: None
    """

    url = 'https://api.electricitymap.org/v3/zones'
    # Perform the API call
    req = requests.get(url)

    # Display country list
    country_map = {}
    for k in req.json():
        zone = req.json()[k]['zoneName']
        country_map[zone] = k

    # Add searchable menu
    entries = list(repeat(0, len(country_map)))
    count = 0
    for k in sorted(country_map):
        entries[count] = k + ' : ' + country_map[k]
        count += 1

    term_menu = TerminalMenu(entries)
    menu_entry_index = term_menu.show()
