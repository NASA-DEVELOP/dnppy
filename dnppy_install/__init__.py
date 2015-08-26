"""
A module for performing common geospatial programming tasks
as part of NASA DEVELOP Projects.

Please consult the dnppy git wiki for further use instructions!
"""

# dnppy version info
__version__ = "1.15.2b0"

# author list
__author__ = ["Jeffry Ely, jwely, jeff.ely.08@gmail.com",
              "Daniel Jensen, djjensen, danieljohnjensen@gmail.com",
              "Lauren Makely, lmakely, lmakely09@gmail.com",
              "Quinten Geddes",
              "Scott Baron"]


# prevents module import issues durring installation.
if not __name__ == "dnppy_install":

    from R_dnppy import *
    from convert import *
    from core import *
    from download import *
    from landsat import *
    from modis import *
    from radar import *
    from raster import *
    from solar import *
    from textio import *
    from time_series import *



