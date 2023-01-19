import time
from bs4 import BeautifulSoup
from selenium import webdriver

# Define url of interest (Italy)
url_electricity_map = "https://app.electricitymaps.com/zone/IT?aggregated=true"

# Set driver of Chrome (required version > 9.0)
driver = webdriver.Chrome('./chromedriver') 
driver.get(url_electricity_map) 
time.sleep(3) #give time for dynamic text to load
html = driver.page_source

# Find carbon intensity data on left panel
soup = BeautifulSoup(html, "html.parser")
carbon_intensity_square = soup.find_all("p", attrs={"data-test-id": "co2-square-value"})
carbon_intensity_value = carbon_intensity_square[0].text
print("Italy Carbon Intensity: {0} (gCO₂eq/kWh)".format(carbon_intensity_value))