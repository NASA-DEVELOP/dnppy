# local imports
from dnppy import raster

# arcpy imports
import arcpy
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    arcpy.env.overwriteOutput = True


def define_projection(filenames):
    """
    Give raster(s) proper MODIS sinusoidal projection metadata

    filename may be either a single filepath string or a list of them.
    """

    # accept list of filenames
    filenames = raster.enf_rastlist(filenames)
    
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

    for filename in filenames:
        arcpy.DefineProjection_management(filenames, proj)
        
    return
