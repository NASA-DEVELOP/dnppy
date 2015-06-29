__author__ = 'jwely'
__all__ = ["null_define"]

import arcpy
from enf_rastlist import enf_rastlist

def null_define(rastlist, NoData_Value):
    """
    Simple batch NoData setting function. Makes raster data more arcmap viewing friendly

     Function inputs a list of raster (usually tifs) files and sets no data values. This
     function does not actually change the raster values in any way, and simply defines which
     numerical values to be considered NoData in metadata.

     inputs:
       rastlist        list of files for which to set NoData values. easily created with
                       "core.list_files" function
       NoData_Value    Value to declare as NoData (usually 0 or -9999)
       Quiet           Set Quiet to 'True' if you don't want anything printed to screen.
                       Defaults to 'False' if left blank.
    """

    rastlist = enf_rastlist(rastlist)

    # iterate through each file in the filelist and set nodata values
    for rastname in rastlist:

        arcpy.SetRasterProperties_management(rastname,data_type="#",statistics="#",
                    stats_file="#",nodata="1 "+str(NoData_Value))

        print("Set nulls in {0}".format(rastname))
    return