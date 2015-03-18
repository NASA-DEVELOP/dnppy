# dnppy

###Overview
DEVELOP National Program Python Package (dnppy)

This collection of python modules serves as a living codebase
for the DEVELOP National Program. Teams in the NASA DEVELOP program increasingly 
find themselves using some level of programming to manipulate project data. 
Most of the time, this data manipulation is performed in Python. The DEVELOP 
Python package, referred to as “dnppy” (done py) was created to improve institutional 
knowledge retention, open the DEVELOP toolkit for public contributions and 
use, represent DEVELOP in the public domain, and put more power in the hands 
of new participants the first day the walk into the program. It is a joint 
social media and programming capacity building endeavor.

For more information about the NASA DEVELOP program and the projects teams conduct 
utilizing NASA Earth Observation Data for society please visit: http://develop.larc.nasa.gov/

#####Instalation
Run "setup.py"

#####Dependencies

Most dependenices come natively with Arcmap 10.2+ . Expect future dependencies from the SciPy stack, which ships with Arcmap 10.3+

1. Python 2.7
2. arcpy  (see ESRI's ArcMap software)
3. numpy

##Development Strategy

#####Scope

This dnppy repository is meant to be an evolving codebase for use by DEVELOP participants as well as end users. All code should be directly relevant to DEVELOP projects. The structure is tailored for us in an ArcMap environment, and should minimize external dependencies outside the python modules shipped with ArcMap 10.3, which includes python 2.7 and the SciPy stack. However, since Arcmap also allows R scripts to be used as Arcmap tools, it may be appropriate to include R scripts within dnppy. General goals are as follows:

1. Make life easier for the participant
2. Provide useful tools for end users
3. Provide useful tools for the geospatial community 

#####Methods

There are some best practices for coding python modules and scripts for use as Arcmap toolboxes, and every effort to adhere to them should be made. This includes using a distutils based distribution method so the dnppy module automatically gets placed in the Arcmap installed python directory so it loads effortlessly as a “native” toolbox. Additional details will be provided through GitHub examples here.

#####Key Functionality
1.	Make NASA data easier to find, download, and use in geospatial environment
2.	Make ancillary data sets such as those provided by NOAA easier to use in conjunction with NASA data products
3.	Build up flexible and robust software tools for data analysis to allow DEVELOP to handle increasingly complex projects over time
4.	Package suitable DEVELOP code for end users to easily deploy
5.	Preserve an educational context and decent help documentation
6.	Preserve the testing framework that’s been implemented to ensure quality and reliability
7.	Keep an open but consistent framework for easy addition of new content
