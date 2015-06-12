# dnppy

###Overview
DEVELOP National Program Python Package (`dnppy`)

This collection of python modules serves as a living codebase
for the DEVELOP National Program. Teams in the DEVELOP program increasingly find themselves using some level of programming to manipulate project data. Most of the time, this data manipulation is performed in Python. The DEVELOP Python package, referred to as “dnppy” (pronounced "done-py" as it uses Python to get the job done) was created to improve institutional knowledge retention, open the DEVELOP toolkit for public contributions and use, represent DEVELOP in the public domain, and put more power in the hands of new participants the first day the walk into the program. It is a social media, programming capacity building, and educational endeavor.

For more information about the NASA DEVELOP program and the projects teams conduct 
utilizing NASA Earth Observation Data for society please visit: http://develop.larc.nasa.gov/

#####Instalation
Run `setup.py`

#####Dependencies

Before dnppy can be installed, ESRI's Arcmap 10.2 or 10.3 must already be installed. ArcMap ships with a custom installation of python 2.7, and `dnppy` is built to modify that python installation.

1. Python 2.7
2. `arcpy`  (see ESRI's ArcMap software)

At present, the following dependencies are automatically installed with the setup file in the pre-existing ArcGIS python directory. GDAL is among them, and dnppy functions will become increasingly GDAL dependent as time goes on.

3. `pip`
4. `wheel`
5. `requests`
5. `gdal`
