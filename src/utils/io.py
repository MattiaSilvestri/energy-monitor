import os
import yaml
import re
import sys


def safe_read_config(config_file: str) -> dict:
    """
    Read the content of the specified config file starting from any path. Then check if the values contained in the configuration file are consistent with the application.

    :param config_file: filename of the .yml config file to read
    :type config_file: str
    :return: configuration file dictionary
    :rtype: dict
    """

    # Extract user absolute path to config file
    path = os.path.dirname(__file__)
    custom_abs_path = os.path.join(path.split("src")[0], "config", config_file)

    # Safe load yaml
    with open(custom_abs_path, "r") as stream:
        config_dict = yaml.safe_load(stream)

    errors = is_config_safe(config_dict)
    error_message = "CONFIGURATION ERORR! There is a problem with some values in the configuration files, please make the appropriate changes following these instructions:\n"
    if errors:
        print(error_message + errors)
        sys.exit()

    return config_dict


def is_config_safe(config_dict: dict) -> str:
    """
    Check if the values contained in the configuration file are consistent with the application, if not return errors descriptions and suggestions on how to solve the issues

    :param config_file: configuration file dictionary
    :type config_file: dict
    :return: list of errors descriptions and suggestions on how to solve the issues
    :rtype: str
    """
    errors = []

    # General numbers requirements
    is_number_reqs = [
        "cpu_retrieval_time",
        "cpu_retrieval_time_decrement",
        "co2_emissions_precision",
        "window_font_size",
        "num_x_points",
        "num_x_ticks",
        "font_size",
        "grid_line_width",
        "line_alpha",
        "area_alpha",
    ]
    errors += recursively_check_nested_dict(
        config_dict, is_number_reqs, is_positive_number
    )

    # Normalized numbers requirements
    is_norm_number_reqs = ["line_alpha", "area_alpha"]
    errors += recursively_check_nested_dict(
        config_dict, is_norm_number_reqs, is_normalized_number
    )

    # Time-letters requirements
    is_time_letter_reqs = ["x_unit_measurement", "y_unit_measurement"]
    errors += recursively_check_nested_dict(
        config_dict, is_time_letter_reqs, is_time_letter
    )

    # List of numbers requirements
    is_list_num_reqs = ["plot_position"]
    errors += recursively_check_nested_dict(
        config_dict, is_list_num_reqs, is_number_list
    )

    # Hex color requirements
    is_color_hex_reqs = ["grid_line_color", "line_color", "area_color"]
    errors += recursively_check_nested_dict(
        config_dict, is_color_hex_reqs, is_color_hex
    )

    # Special reqs
    error = is_font(config_dict["Appearance"]["Plot"]["font_weight"])
    if error:
        errors += f"font_weight {error}"
    error = is_line_style(config_dict["Appearance"]["Plot"]["grid_line_style"])
    if error:
        errors += f"grid_line_style {error}"

    # Format error list into readable string
    error_string = "\n".join(["* " + e for e in errors])

    return error_string


def recursively_check_nested_dict(
    d: dict, params_to_check: list, checker_function: callable
) -> list:
    """
    Recursive function that returns a list of errors by taking a dictionary,
    a checker function and a list of parameters where to apply this function

    :param d: dictionary where you want to perform the checks
    :type d: dict
    :param params_to_check: list of parameters to check with the checker function
    :type params_to_check: list
    :param checker_function: function to find errors in the configuration parameters
    :type checker_function: callable
    :return: list of errors descriptions and suggestions on how to solve the issues
    :rtype: list

    """
    level_errors = []

    for param, value in zip(d.keys(), d.values()):
        if isinstance(value, dict):
            k_errors = recursively_check_nested_dict(
                value, params_to_check, checker_function
            )
            level_errors += k_errors
        else:
            if param in params_to_check:
                error = checker_function(d[param])
                if error:
                    level_errors.append(f"{param} {error}")

    return level_errors


def is_positive_number(value) -> str:
    if isinstance(value, (float, int)):
        if value > 0:
            return ""
    return f"must be a positive number. Got '{str(value)}' instead."


def is_normalized_number(value) -> str:
    if isinstance(value, (float, int)):
        if value >= 0 and value <= 1:
            return ""
    return f"must be a number between 0 and 1. Got '{str(value)}' instead."


def is_time_letter(value) -> str:
    if isinstance(value, str):
        if value in ["s", "m", "h"]:
            return ""
    return f"must be a string between ['s', 'm', 'h']. Got '{str(value)}' instead."


def is_number_list(value) -> str:
    if isinstance(value, list):
        for el in value:
            if not isinstance(el, (float, int)):
                return f"must be a list of numbers. Got '{str(value)}' instead."
        return ""
    else:
        return f"must be a list of numbers. Got '{str(value)}' instead."


def is_color_hex(value) -> str:
    if isinstance(value, str):
        match = re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", value)
        if match:
            return ""
    return f"must be a string representing a hex color code (e.g. #ffffff). Got '{str(value)}' instead."


def is_font(value) -> str:
    if isinstance(value, str):
        if value in ["normal", "bold", "heavy", "light", "ultrabold", "ultralight"]:
            return ""
    return f"must be a string between ['normal', 'bold', 'heavy', 'light', 'ultrabold', 'ultralight']. Got '{str(value)}' instead."


def is_line_style(value) -> str:
    if isinstance(value, str):
        if value in ["-", "--", "-.", ":"]:
            return ""
    return (
        f"must be a string between ['-', '--', '-.', ':']. Got '{str(value)}' instead."
    )
