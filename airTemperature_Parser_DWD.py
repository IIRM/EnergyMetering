import csv
import pandas as pd

__author__ = "Dr Nancy Retzlaff"
__copyright__ = "Copyright 2007, The Cogent Project"
__credits__ = ["Nancy Retzlaff"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Dr Nancy Retzlaff"
__email__ = "retzlaff@wifa.uni-leipzig.de"
__status__ = "Prototype"

# download data for air temperature from DWD
# 1. find name of closest measuring station here
#   https://www.dwd.de/DE/fachnutzer/landwirtschaft/appl/stationskarte/_node.html
# 2. find ID of this station here:
#   https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/air_temperature/historical/TU_Stundenwerte_Beschreibung_Stationen.txt
# 3. download respective data

weatherStation_ = ''  # todo set id

incompletePath = 'data/produkt_tu_stunde_'

temperature = []
humidity = []
date = []


def getData(city):  # todo in case of several cities set station ids here
    global weatherStation_
    if city == "city1":
        weatherStation_ = ''
    elif city == "city2":
        weatherStation_ = ''
    else:
        print("invalid city. Setting default value.")
    filePath = incompletePath + weatherStation_ + '.txt'
    file = open(filePath, "r")
    file_reader = csv.reader(file, delimiter=";")
    next(file_reader)
    for line in file_reader:
        # file structure:
        # stationID; yyyymmddhh; ??; temperature; relative humidity; eor?
        date.append(line[1].strip())
        temperature.append(float(line[3].strip()))
        humidity.append(float(line[4].strip()))
    file.close()
    data = pd.DataFrame(columns=["date", "temperature", "humidity"])
    data["date"] = date
    data["temperature"] = temperature
    data["humidity"] = humidity
    return data
