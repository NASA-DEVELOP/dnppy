__author__ = 'jwely'
__all__ = ["null_set_range"]

from enf_rastlist import enf_rastlist
from to_numpy import to_numpy
from from_numpy import from_numpy

import arcpy

def null_set_range(rastlist, high_thresh = None, low_thresh = None, NoData_Value = None):
    """
    Changes values within a certain range to NoData. similar to ``raster.null_define``,
    but can take an entire range of values to set to NoData. useful in filtering
    obviously erroneous high or low values from a raster dataset.

    :param rastlist:     list of rasters for which to set no dta values
    :param high_thresh:  will set all values above this to  NoData
    :param low_thresh:   will set all values below this to NoData

    :return rastlist:    list of all rasters modified by this function
    """

    # sanitize filelist input
    rastlist = enf_rastlist(rastlist)

    # iterate through each file in the filelist and set nodata values
    for rastname in rastlist:

        #load raster as numpy array and save spatial referencing.
        rast, meta = to_numpy(rastname)

        if not NoData_Value is None:
            NoData_Value = meta.NoData_Value

        if not high_thresh is None:
            rast[rast >= high_thresh] = NoData_Value

        if not low_thresh is None:
            rast[rast <= low_thresh] = NoData_Value

        from_numpy(rast, meta, rastname)
        try:
            arcpy.SetRasterProperties_management(rastname, data_type = "#", statistics = "#",
                    stats_file = "#", nodata = "1 " + str(NoData_Value))
        except RuntimeError:
            print("failed to set nodata in {0}".format(rastname))

    return