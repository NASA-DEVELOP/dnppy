
# standard imports
import sys
import os

# dnppy imports
from dnppy import core

# arcpy imports
import arcpy
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    from arcpy.sa import *
    from arcpy import env
    arcpy.env.overwriteOutput = True


__all__ = ["GCMO_NetCDF"]


def GCMO_NetCDF(netcdf_list, variable, outdir):
    """
    Extracts all time layers from a "Global Climate Model Output" NetCDF layer

    Inputs:
        netcdf_list     list of netcdfs from CORDEX climate distribution
        varaible        the climate variable of interest (tsmax, tsmin, etc)
        outdir          output directory to save files.
    """

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    netcdf_list = core.enf_list(netcdf_list)

    for netcdf in netcdf_list:
        # get net cdf properties object
        props = arcpy.NetCDFFileProperties(netcdf)
        
        print("finding dimensions")
        dims  = props.getDimensions()
        for dim in dims:
            print dim, props.getDimensionSize(dim)

        # make sure the variable is in this netcdf
        if variable:
            if not variable in props.getVariables():
                print("Valid variables for this file include {0}".format(props.getVariables()))
                raise Exception("Variable '{0}' is not in this netcdf!".format(variable))

        for dim in dims:
            if dim == "time":

                # set other dimensions
                x_dim = "lon"
                y_dim = "lat"
                band_dim = ""
                valueSelectionMethod = "BY_VALUE"
                
                size = props.getDimensionSize(dim)
                for i in range(size):

                    # sanitize the dimname for invalid characters
                    dimname = props.getDimensionValue(dim,i).replace(" 12:00:00 PM","")
                    dimname = dimname.replace("/","-").replace(" ","_")
                    
                    dim_value = [["time", props.getDimensionValue(dim,i)]]
                    print("extracting '{0}' from '{1}'".format(variable, dim_value))

                    outname = core.create_outname(outdir, netcdf, dimname, 'tif')
                    
                    arcpy.MakeNetCDFRasterLayer_md(netcdf, variable, x_dim, y_dim, "temp",
                                                   band_dim, dim_value, valueSelectionMethod)
                    arcpy.CopyRaster_management("temp", outname, "", "", "", "NONE", "NONE", "")
                    
    return
