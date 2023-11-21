![Python](https://img.shields.io/badge/python-3670A0?logo=python&logoColor=ffdd54)
![macOS](https://img.shields.io/badge/mac%20os-000000?logo=macos&logoColor=F0F0F0)
![Linux](https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black)
![Windows](https://img.shields.io/badge/Windows-0078D6?logo=windows&logoColor=white)

![Logo](./media/energy-monitor-logo.png)

# **Energy-monitor**
Simple python tool to monitor your personal computer CO<sub>2</sub> emissions. 

Generates a graph displaying the amount of grams of [CO<sub>2</sub>-equivalent](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:Carbon_dioxide_equivalent) per unit of time emitted by your PC while is running. <br>
Essentially, the graph shows the "carbon footprint" of your PC. <br>
Grams of CO<sub>2</sub>-equivalent/time can be understood as the amount of emissions that the computer would generate if it continued running at the same rate for the specified time. Using a metaphor, is a measure akin to km/h in cars, which indicate the amount of kilometers that would be travelled in one hour if the speed is kept constant. <br>

The amount of grams CO<sub>2</sub>-equivalent is computed according to the [Thermal Design Power (TDP)](https://en.wikipedia.org/wiki/Thermal_design_power) of your CPU and adjusted to the carbon intensity in your current location, a measure of the greenhouse gas emissions associated with producing the electricity you consume. <br>

## **Table of contents**
* [Features](#features)
* [Documentation](#documentation)
* [Installation](#installation)
* [Example usage](#example)
* [References](#references)
* [To do's](#to-dos)

## **Features**
* Compute CO<sub>2</sub> emissions of the personal computer based on TDP and current location;
* Display the CO<sub>2</sub> emissions with fully customizable graph (e.g., temporal resolution, color, etc.);
* Works on different Operating Systems;
* ...;

## **Documentation**
The program can be run from the command line as follows:
```
energy-monitor
```

The program asks the user to accept using their own current location to determine the carbon impact in the area (based on [Electricity Maps](https://app.electricitymaps.com/map)). <br>
If the user does not accept, the user will be asked to select from a list the country. <br>
The program will then retrieve the TDP of the CPU. <br>
A graph will be displayed showing the CO<sub>2</sub> emissions of the PC over time (default resolution: 1 second). <br>


## **Installation**
### Option 1: From PyPI
```
pip install energy-monitor
```
### Option 2: From source
```
pip install git@https://github.com/MattiaSilvestri/energy-monitor.git
```

After installation, the package needs API keys from the following services:
* [Co2Signal](https://www.co2signal.com/) (free)
* [ipgeolocation](https://ipgeolocation.io/) (free)
These API keys can be obtained for free by registering to the services. <br>
Once obtained, they need to be stored in ./config/secrets.yml

## **Example**

![example](./media/energy-monitor-example.gif)


## **Acknowledgements**
We made extensive use of external python packages, listed in the [requirements.txt](https://github.com/MattiaSilvestri/energy-monitor/blob/readme/requirements.txt) file. <br>
Moreover, the app makes use of publicly available tools, such as:
- [Electricity Maps](https://app.electricitymaps.com/map)
- [Co2Signal API](https://www.co2signal.com/)

## **To do's**
- [ ] Forecasting
- [ ] Give a reference about how much CO2 is being used (i.e. as compared to
      using the washing machine)
- [ ] Personal history
