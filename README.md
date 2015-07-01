# dnppy

###Overview
DEVELOP National Program Python Package (`dnppy`)

This collection of python modules serves as a living codebase
for the DEVELOP National Program. Teams in the DEVELOP program increasingly find themselves using some level of programming to manipulate project data. Most of the time, this data manipulation is performed in Python. The DEVELOP Python package, referred to as “dnppy” (pronounced "done-py" as it uses Python to get the job done) was created to improve institutional knowledge retention, open the DEVELOP toolkit for public contributions and use, represent DEVELOP in the public domain, and put more power in the hands of new participants the first day the walk into the program. It is a social media, programming capacity building, and educational endeavor.

For more information about the NASA DEVELOP program and the projects teams conduct 
utilizing NASA Earth Observation Data for society please visit: http://develop.larc.nasa.gov/

####Instalation
Run `setup.py` 

####Dependencies

Before dnppy can be installed, ESRI's Arcmap 10.1+ must already be installed. ArcMap ships with a custom installation of python 2.7, and `dnppy` is built to modify that python installation.

1. Python 2.7
2. `arcpy`  (see ESRI's ArcMap software)

At present, the following third party packages are automatically installed with the setup file in the pre-existing ArcGIS python directory. Windows binaries for each of these resources were selected from [here](http://www.lfd.uci.edu/~gohlke/pythonlibs) and rehosted in the dnppy release assets. They are unofficial,  and are included only to provide convenient installation of common scientific packages for the custom ArcMap installation of python.

3. `pip`
4. `wheel`
5. `requests`
6. `numpy 1.9.2`
7. `gdal`
8. `h5py`

In each case, 64 bit binaries will be used if the target python installation is 64 bit. For most intended Arcmap users, this means 64 bit binaries will only be installed if the "64 bit background geoprocessing" add-in is available.
