__author__ = 'jwely'

"""
This script is simply a list of projection strings for
some common projections that are needed for unzipping
uncommon file formats. All of this projection info
can be found at [http://spatialreference.org/]
and downloaded by clicking the link to the .prj file

PLEASE add to this
"""

SOURCE = "http://spatialreference.org/"

def WGS_1984():
    string =   '''GEOGCS["GCS_WGS_1984",
                DATUM["D_WGS_1984",
                SPHEROID["WGS_1984",6378137,298.257223563]],
                PRIMEM["Greenwich",0],
                UNIT["Degree",0.017453292519943295]]'''
    return string


def Arctic_Polar_Sterographic():
    string = '''PROJCS["WGS 84 / Arctic Polar Stereographic",
                GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",
                SPHEROID["WGS_1984",6378137,298.257223563]],
                PRIMEM["Greenwich",0],
                UNIT["Degree",0.017453292519943295]],
                PROJECTION["Stereographic_North_Pole"],
                PARAMETER["standard_parallel_1",71],
                PARAMETER["central_meridian",0],
                PARAMETER["scale_factor",1],
                PARAMETER["false_easting",0],
                PARAMETER["false_northing",0],
                UNIT["Meter",1]]'''
    return string


def Antarctic_Polar_Sterographic():
    string = '''PROJCS["WGS 84 / Antarctic Polar Stereographic",
                GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",
                SPHEROID["WGS_1984",6378137,298.257223563]],
                PRIMEM["Greenwich",0],
                UNIT["Degree",0.017453292519943295]],
                PROJECTION["Stereographic_South_Pole"],
                PARAMETER["standard_parallel_1",-71],
                PARAMETER["central_meridian",0],
                PARAMETER["scale_factor",1],
                PARAMETER["false_easting",0],
                PARAMETER["false_northing",0],
                UNIT["Meter",1]]'''

    return string