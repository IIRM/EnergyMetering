# EnergyMetering

Before compiling the code, please make sure you installed python and pip correctly. 
The code was  compiled with Python compiler version 3.9; packaged installed with pip 21.2.4.

You can test the versions in the terminal

```shell script
pip -V
python --version
```

## Before you start

In order to compile the code successfully you need to install the packages used. Therefore open 
the terminal and run:

```shell script
pip install pandas, numpy, matplotlib, statistics
```

## Energy Consumption Data
The code was developed for consumption data per quarter of an hour. Inputting other data potentially
leads to incorrect results, most likely even runtime errors. Make sure the data you input can be read
by the script. The input file format chosen was the one used in EnEffCo (https://www.eneffco.de/en/energy-effiency/).

The first two columns denote the time steps "From" and "To". Only "From" is used throughout runtime as
it contains the information about the time and date (in format "%d.%m.%Y %H:%M"), making "To" 
redundant. If your input data contains a different format please make respective adjustments in
'dateAndTime.py'. All other columns of the input contain RLM data for different meters.

Please note that the input currently contains a second row with redundant information which is
dropped.


## Weather Data
In order to check whether the weather, i.e. temperature and humidity, has any influence on the energy 
consumption of a building, please download the data from the German Weather Agency (DWD). In case
your building is not located in Germany please make sure the data used is in a similar format.

### Using the correct data correctly

1. In order to find the closest weather station to your location of interest please see this map: 
https://www.dwd.de/DE/fachnutzer/landwirtschaft/appl/stationskarte/_node.html

2. Clicking on the weather station will give you the correct name which in return can be used to
find the station ID in the station list (https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/air_temperature/historical/TU_Stundenwerte_Beschreibung_Stationen.txt)
. 
3. Download the correct weather info ('stundenwerte_TU_' + station_ID + '_hist.zip), unzip it and 
save the file 'produkt_tu_stunde_' + station_ID + '.txt' in the data folder. You will not 
need any other files.

4. Set weatherStation_ in airTemperature_Parser_DWD.py to the station_ID value

## MIT Licence
Copyright 2021 Kilowatthandel AG

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the 
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit 
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the 
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE 
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

