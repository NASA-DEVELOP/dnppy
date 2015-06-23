__author__ = 'jwely'

"""
This script is siply a list of projection strings for some
common projections
"""

def WGS_1984():
    string =  '''GEOGCS["GCS_WGS_1984",
                DATUM["D_WGS_1984",
                SPHEROID["WGS_1984",6378137,298.257223563]],
                PRIMEM["Greenwich",0],
                UNIT["Degree",0.017453292519943295]]'''
    return string