"""
The DEVELOP national Program python package (dnppy) is a living codebase for the
NASA DEVELOP program, our project partners, and the GIS programming community!
DEVELOP is under NASA's "Capacity Building" program, and functions to educate its
participants and partners in earth science and remote sensing.

Please consult the dnppy documentation pages for further information!
"""

# dnppy version. follows [major revision].[year].[minor revision]
__version__= "1.15.2"

# author list
__author__ = ["Jeffry Ely, jwely, jeff.ely.08@gmail.com",
              "Daniel Jensen, djjensen, danieljohnjensen@gmail.com",
              "Lauren Makely, lmakely, lmakely09@gmail.com",
              "Quinten Geddes",
              "Scott Baron",
              ]


# prevents module import issues during installation.
if not __name__ == "dnppy_install":

    #from test import *
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



