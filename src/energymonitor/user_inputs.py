#!/usr/bin/env python3

import argparse

# TODO: map country to countrycode
# TODO: display list of countries

help_message = 'It collects CO2 emissions data from your country and compare \
it with your energy consumption to produce an estimate of the CO2 generated \
by your computer.'
parser = argparse.ArgumentParser(description=help_message)

def get_country() -> str:
    # TODO: add documentation
    parser.add_argument('--set-country', dest='country', type=str,
                        help='Name of the country')

    args = parser.parse_args()
    return args.country
