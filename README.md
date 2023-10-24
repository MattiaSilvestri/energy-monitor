![Python](https://img.shields.io/badge/python-3670A0?logo=python&logoColor=ffdd54)
![macOS](https://img.shields.io/badge/mac%20os-000000?logo=macos&logoColor=F0F0F0)
![Linux](https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black)
![Windows](https://img.shields.io/badge/Windows-0078D6?logo=windows&logoColor=white)

![Logo](./media/energy-monitor-logo.png)

# **Energy-monitor**
Simple python tool to monitor your personal computer CO<sub>2</sub> emissions. 

Generates a graph displaying the amount of CO<sub>2</sub> emitted by your PC while is running. 
The amount of CO<sub>2</sub> is computed according to the Thermal Design Power (TDP) of your CPU and adjusted to the carbon impact in your current location.

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
