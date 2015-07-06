__author__ = "jwely", "djjensen"
__all__ = ["gap_fill_temporal"]


import os
import numpy as np
from dnppy import core
from dnppy.raster import to_numpy, from_numpy


def gap_fill_temporal(rasterlist, outdir = False):
    """
    This function is designed to input a time sequence of rasters with partial voids and
    output a copy of each input image with every pixel equal to the last good value taken.
    This function will step forward in time through each raster and fill voids from the values
    of previous rasters. The resulting output image will contain all the data that was in the
    original image, with the voids filled with older data. A second output image will be
    generated where the pixel values are equal to the age of each pixel in the image. So
    if a void was filled with data thats 5 days old, the "age" raster will have a value of
    "5" at that location.

    Inputs:
        rasterlist      a list of filepaths for rasters with which to fill gaps
                            *the first item in this list will be the base raster
                            **values will be filled based on the list's ordering
                                (e.g. gap in raster 1 will first attempt to take the corresponding
                                value from raster 2, then 3 if raster 2 also contains a gap there)
        outdir          the path to the desired output folder
                            *optional - left "False" by default
                            **if left "False", the output tiff will be place in the same folder
                                as the first input raster
    """

    #enforce the list of rasters to ensure it's sanitized
    rasterlist = core.enf_filelist(rasterlist)

    #create an empty list to store output arrays in
    arr_list = []

    #convert each raster in the input list to an array, and save its data to the list
    for i, raster in enumerate(rasterlist):
        item = rasterlist[i]
        item_arr = to_numpy(item)
        arr_list.append(item_arr[0].data)

    #convert the list to a numpy array
    arr_list = np.array(arr_list)

    #set the lists of ranges of values for each dimension of the output array
    xrange = range(0, np.shape(arr_list)[2])
    yrange = range(0, np.shape(arr_list)[1])
    zrange = range(0, np.shape(arr_list)[0])

    #pull out the first array to be edited
    new_arr = arr_list[0]

    #loop through each x, y value
    #if the first array's value at each location is "Not A Number",
    #attempt to fill it with the corresponding value from the next array
    #if no array has a corresponding value, it will be left as a "nan"
    for i in yrange:
        for j in xrange:
            if  np.isnan(new_arr[i,j]) == True:
                x = 1
                while x <= zrange[-1]:
                    if np.isnan(arr_list[x,i,j]) == False:
                        new_arr[i,j] = arr_list[x,i,j]
                        break
                    x = x + 1

    #separate the filename from the first input array                
    inname = os.path.splitext(rasterlist[0])[0]

    #create an output name
    if outdir:
        outdir = os.path.abspath(outdir)
        name = "{0}_gapfilled.tif".format(os.path.split(inname)[1])
        outname = os.path.join(outdir, name)
    else:
        outname = "{0}_gapfilled.tif".format(inname)

    #convert the edited array to a tiff
    from_numpy(new_arr, item_arr[1], outname, "NoData")

    return outname