# local imports
from dnppy import raster

# arcpy imports
import arcpy
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    arcpy.env.overwriteOutput = True


def define_projection(file_list):
    """
    Give raster(s) proper MODIS sinusoidal projection metadata.
    Some MODIS data does not have an adequately defined projection
    for some software like arcmap to use

    :param file_list: a list of one or more filepaths
    """

    # accept list of file_list
    file_list = raster.enf_rastlist(file_list)
    
    # custom text for MODIS sinusoidal projection
    proj = """PROJCS["Sinusoidal",
                GEOGCS["GCS_Undefined",
                    DATUM["D_Undefined",
                        SPHEROID["User_Defined_Spheroid",6371007.181,0.0]],
                    PRIMEM["Greenwich",0.0],
                    UNIT["Degree",0.017453292519943295]],
                PROJECTION["Sinusoidal"],
                PARAMETER["False_Easting",0.0],
                PARAMETER["False_Northing",0.0],
                PARAMETER["Central_Meridian",0.0],
                UNIT["Meter",1.0]]"""

    for filename in file_list:
        arcpy.DefineProjection_management(filename, proj)
        
    return
