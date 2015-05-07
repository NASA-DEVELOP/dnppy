# local imports
from dnppy import core


__all__=['define_null',     # complete
         'set_range_null']  # complete


def define_null(rastlist, NoData_Value, Quiet=False):
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

    rastlist = core.enf_rastlist(rastlist)

    # iterate through each file in the filelist and set nodata values
    for rastname in rastlist:

        arcpy.SetRasterProperties_management(rastname,data_type="#",statistics="#",
                    stats_file="#",nodata="1 "+str(NoData_Value))
               
        print("Set nulls in {0}".format(rastname))           
    return



def set_range_null(rastlist, above, below, NoData_Value):
    """
    Changes values within a certain range to NoData
    
     similar to raster.define_null, but can take an entire range of values to set to NoData.
     useful in filtering obviously erroneous high or low values from a raster dataset.

     inputs:
       rastlist    list of files for which to set NoData values. easily created with
                       "core.list_files" function
       above       will set all values above this, but below "below" to NoData
                       set to 'False' if now upper bound exists
       below       will set all values below this, but above "above" to NoData
                       set to 'False' if no lower bound exists
    """

    # sanitize filelist input
    rastlist = enf_rastlist(rastlist)

    # iterate through each file in the filelist and set nodata values
    for rastname in filelist:
        #load raster as numpy array and save spatial referencing.
        raster, meta = to_numpy(rastname)

        if above and below:
            raster[raster <= below and raster >= above] = NoData_Value
        elif above:
            raster[raster >= above] = NoData_Value
        elif below:
            raster[raster <= below] = NoData_Value
            
        raster.from_numpy(raster, meta, filename)
        arcpy.SetRasterProperties_management(rastname, data_type="#",statistics="#",
                    stats_file="#",nodata="1 " + str(NoData_Value))
        
        print("Set NoData values in {0}".format(rastname))
            
    return
