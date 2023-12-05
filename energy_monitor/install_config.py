import shutil
import argparse

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


if __name__ == "__main__":
    install_config()
