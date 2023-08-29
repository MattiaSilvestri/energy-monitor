import os
import yaml

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
    custom_abs_path = os.path.join(path.split("src\\")[0], 'config', config_file)
    
    # Safe load yaml
    with open(custom_abs_path, 'r') as stream:
        config_dict = yaml.safe_load(stream)

    errors = is_config_safe(config_dict)
    if errors: raise Exception(str(errors))

    return config_dict


def is_config_safe(config_dict: dict) -> list[str]:
    """
    Check if the values contained in the configuration file are consistent with the application, if not return errors descriptions and suggestions on how to solve the issues

    :param config_file: configuration file dictionary
    :type config_file: dict
    :return: list of errors descriptions and suggestions on how to solve the issues
    :rtype: list
    """

    config_functional = config_dict["Functional"]
    config_appearance_window = config_dict["Appearance"]["Window"]
    config_appearance_plot = config_dict["Appearance"]["Plot"]
    errors = []

    # General numbers requirements
    is_number_reqs = ["cpu_retrieval_time", "cpu_retrieval_time_decrement", "co2_emissions_precision", 
                      "window_font_size", "num_x_points", 
                      "num_x_ticks", "font_size", "grid_line_width", "line_alpha", "area_alpha"]
    for parameter in is_number_reqs:
        if parameter in config_functional.keys(): error = is_number(config_functional[parameter])
        if parameter in config_appearance_window.keys(): error = is_number(config_appearance_window[parameter])
        if parameter in config_appearance_plot.keys(): error = is_number(config_appearance_plot[parameter])
        if error: errors.append(f"{parameter} {error}")

    # Time-letters requirements
    is_time_letter_reqs = ["x_unit_measurement", "y_unit_measurement"]
    for parameter in is_time_letter_reqs:
        if parameter in config_functional.keys(): error = is_time_letter(config_functional[parameter])
        if parameter in config_appearance_window.keys(): error = is_time_letter(config_appearance_window[parameter])
        if parameter in config_appearance_plot.keys(): error = is_time_letter(config_appearance_plot[parameter])
        if error: errors.append(f"{parameter} {error}")

    # List of numbers requirements
    is_list_num_reqs = ["plot_position"]
    for parameter in is_list_num_reqs:
        if parameter in config_functional.keys(): error = is_number_list(config_functional[parameter])
        if parameter in config_appearance_window.keys(): error = is_number_list(config_appearance_window[parameter])
        if parameter in config_appearance_plot.keys(): error = is_number_list(config_appearance_plot[parameter])
        if error: errors.append(f"{parameter} {error}")

    # List of numbers requirements
    is_list_num_reqs = ["plot_position"]
    for parameter in is_list_num_reqs:
        if parameter in config_functional.keys(): error = is_number_list(config_functional[parameter])
        if parameter in config_appearance_window.keys(): error = is_number_list(config_appearance_window[parameter])
        if parameter in config_appearance_plot.keys(): error = is_number_list(config_appearance_plot[parameter])
        if error: errors.append(f"{parameter} {error}")

    error_string = "\n".join(["* " + e for e in errors])
    
    return error_string





def is_number(value) -> str:
    if isinstance(value, (float, int)):
        return ""
    else:
        return f"must be a number. Got '{str(value)}' instead."
    
def is_time_letter(value) -> str:
    if isinstance(value, str):
        if value.lower() in ['s', 'm', 'h']:
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