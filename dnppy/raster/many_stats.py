__author__ = "Jwely"
__all__ = ["many_stats"]

from dnppy import core
from enf_rastlist import enf_rastlist
from to_numpy import to_numpy
from from_numpy import from_numpy
from raster_fig import raster_fig

# other imports
import numpy
import os

def many_stats(rasterlist, outdir, outname, saves = None, low_thresh = None,
                    high_thresh = None, numtype = 'float32', NoData_Value = -9999):
    """
    Take statistics across many input rasters
    
     this function is used to take statistics on large groups of rasters with identical
     spatial extents. Similar to Rolling_Raster_Stats

     Inputs:
        rasterlist      list of raster filepaths for which to take statistics
        outdir          directory where output should be stored.
        outname         output name filename string that will be used in output filenames
        saves           which statistics to save in a raster. In addition to the options
                        supported by 
                           
                        Defaults to all three ['AVG','NUM','STD'].
        low_thresh      values below low_thresh are assumed erroneous and set to NoData
        high_thresh     values above high_thresh are assumed erroneous and set to NoData.
        numtype         type of numerical value. defaults to 32bit float.
    """

    if saves is None:
        saves = ['AVG','NUM','STD','SUM']
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    
    rasterlist = enf_rastlist(rasterlist)

    # build the empty numpy array based on size of first raster
    temp_rast, metadata = to_numpy(rasterlist[0])
    xs, ys              = temp_rast.shape
    zs                  = len(rasterlist)
    rast_3d             = numpy.zeros((xs,ys,zs))

    metadata.NoData_Value = numpy.nan

    # open up the initial figure
    rastfig = raster_fig(temp_rast)

    # populate the 3d matrix with values from all rasters
    for i, raster in enumerate(rasterlist):

        # print a status and open a figure
        print('working on file {0}'.format(os.path.basename(raster)))
        new_rast, new_meta  = to_numpy(raster, numtype)

        new_rast = new_rast.data

        if not new_rast.shape == (xs, ys):
            print new_rast.shape

        # set rasters to have 'nan' NoData_Value
        if new_meta.NoData_Value != metadata.NoData_Value:
            new_rast[new_rast == new_meta.NoData_Value] = metadata.NoData_Value
            
        # set values outside thresholds to nodata values
        if not low_thresh is None:
            new_rast[new_rast < low_thresh] = metadata.NoData_Value
        if not high_thresh is None:
            new_rast[new_rast > high_thresh] = metadata.NoData_Value

        new_rast = numpy.ma.masked_array(new_rast, numpy.isnan(new_rast))

        # display a figure
        rastfig.update_fig(new_rast)

        rast_3d[:,:,i] = new_rast

    # build up our statistics by masking nan values and performing matrix operations
    rastfig.close_fig()
    rast_3d_masked  = numpy.ma.masked_array(rast_3d, numpy.isnan(rast_3d))

    if "AVG" in saves:
        avg_rast        = numpy.mean(rast_3d_masked, axis = 2)
        avg_rast        = numpy.array(avg_rast)
        rastfig         = raster_fig(avg_rast, title = "Average")

        avg_name = core.create_outname(outdir, outname, 'AVG', 'tif')
        print("Saving AVERAGE output raster as {0}".format(avg_name))
        from_numpy(avg_rast, metadata, avg_name, NoData_Value = NoData_Value)
        rastfig.close_fig()
        del avg_rast

    if "STD" in saves:
        std_rast        = numpy.std(rast_3d_masked, axis = 2)
        std_rast        = numpy.array(std_rast)
        rastfig         = raster_fig(std_rast, title = "Standard Deviation")

        std_name = core.create_outname(outdir, outname, 'STD', 'tif')
        print("Saving STANDARD DEVIATION output raster as {0}".format(std_name))
        from_numpy(std_rast, metadata, std_name, NoData_Value = NoData_Value)
        rastfig.close_fig()
        del std_rast
        
    if "NUM" in saves:
        num_rast        = (numpy.zeros((xs,ys)) + zs) - numpy.sum(rast_3d_masked.mask, axis = 2)
        num_rast        = numpy.array(num_rast)
        rastfig         = raster_fig(num_rast, title =  "Good pixel count (NUM)")
        rastfig.close_fig()

        num_name = core.create_outname(outdir, outname, 'NUM', 'tif')
        print("Saving NUMBER output raster as {0}".format(num_name))
        from_numpy(num_rast, metadata, num_name, NoData_Value = NoData_Value)
        rastfig.close_fig()
        del num_rast

    if "SUM" in saves:
        sum_rast        = numpy.sum(rast_3d_masked, axis = 2)
        sum_rast        = numpy.array(sum_rast)
        rastfig         = raster_fig(sum_rast, title = "Good pixel count (NUM)")
        rastfig.close_fig()

        sum_name = core.create_outname(outdir, outname, 'SUM', 'tif')
        print("Saving NUMBER output raster as {0}".format(sum_name))
        from_numpy(sum_rast, metadata, sum_name, NoData_Value = NoData_Value)
        rastfig.close_fig()
        del sum_rast
                   
    rastfig.close_fig()

    return
