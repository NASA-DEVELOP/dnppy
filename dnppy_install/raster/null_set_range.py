__author__ = 'jwely'

from enf_rastlist import enf_rastlist
from to_numpy import to_numpy

import arcpy


def null_set_range(rastlist, above, below, NoData_Value = False):
    """
    Changes values within a certain range to NoData

     similar to raster.null_define, but can take an entire range of values to set to NoData.
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
    for rastname in rastlist:
        #load raster as numpy array and save spatial referencing.
        raster, meta = to_numpy(rastname)

        if not NoData_Value:
            NoData_Value = meta.NoData_Value

        if above and below:
            raster[below >= raster >= above] = NoData_Value
        elif above:
            raster[raster >= above] = NoData_Value
        elif below:
            raster[raster <= below] = NoData_Value

        raster.from_numpy(raster, meta, rastname)
        arcpy.SetRasterProperties_management(rastname, data_type="#",statistics="#",
                    stats_file = "#",nodata = "1 " + str(NoData_Value))

        print("Set NoData values in {0}".format(rastname))

    return