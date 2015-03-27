



def define_projection(filename):

    """Give raster proper MODIS sinusoidal projection metadata"""
    
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

    arcpy.DefineProjection_management(filename, proj)

    return
