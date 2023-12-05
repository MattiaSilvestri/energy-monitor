import shutil
import argparse
import json
import os
import sys

help_message = "It copies the default config folder to the folder specified by \
the user"
parser = argparse.ArgumentParser(description=help_message)


def install_config():
    # Get filepath from user
    parser.add_argument(
        # "filename",
        metavar="F",
        type=str,
        dest="filename",
        help="Where to save the config file",
    )

    args = parser.parse_args()

    # Define the source path of the config files within your package
    source_path = "./config/config.yml"

    # Define the destination path where you want to copy or move the config files on the target system
    destination_path = args.filename

    # Copy or move the config files
    try:
        shutil.copyfile(source_path, destination_path)
        print("Config files have been installed successfully.")
    except Exception as e:
        print(f"An error occurred while installing config files: {e}")

    # Write user path in json file
    path = os.path.join(
        os.path.dirname(__file__).split("energy_monitor")[0],
        "energy_monitor",
        "data",
    )
    # define file name of the output file
    json_fname = os.path.join(path, "user_data.json")
    if os.path.isfile(json_fname) and not "pytest" in sys.modules:
        # load json file with the cpu tdp info
        with open(json_fname, "r") as f:
            user_data = json.load(f)

        user_data["user_config"] = args.filename

        with open(json_fname, "w") as f:
            json.dump(user_data, f)


if __name__ == "__main__":
    install_config()
