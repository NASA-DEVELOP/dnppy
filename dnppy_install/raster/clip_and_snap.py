__author__ = 'jwely'

from to_numpy import to_numpy
from from_numpy import from_numpy

import os
import arcpy
import numpy
import shutil

def clip_and_snap(snap_raster, rastname, outname, numtype = False , NoData_Value = False):
    """
    Ensures perfect coincidence between a snap_raster and any input rasters

     This script is primarily intended for calling by the "raster.spatially_match" function
     but may be called independently.

     it is designed to input a reference image and a working image. The working image must
     be in exactly the same projection and spatial resolution as the reference image. This
     script will simply ensure the tif files are perfectly coincident, and that the total image
     extents are identical. This is important when performing numpy manipulations on matrices
     derived from different datasets manipulated in different ways to ensure alignment.

     This script makes modifications to the original raster file, so save a backup if you are
     unsure how to use this.

     inputs:
       snap_raster     filepath and name of reference raster whos extent will be taken on by
                       the input rastername
       rastname        name of raster file which should be snapped to the snap_raster
       NoData_Value    Value desired to represent NoData in the saved image.

     outputs:
       snap_meta       metadata of the snap_raster file as output by to_numpy
       meta            metadata of the rastername file as output by to_numpy
    """

    # grab metadata for rastname
    _,snap_meta = to_numpy(snap_raster)
    _,meta      = to_numpy(rastname)

    if not NoData_Value:
        NoData_Value = meta.NoData_Value

    if not numtype:
        numtype = 'float32'

    head,tail   = os.path.split(outname)
    tempdir     = os.path.join(head, 'temp')

    if not os.path.isdir(tempdir):
        os.makedirs(tempdir)

    # set the snap raster environment in arcmap.
    arcpy.env.snapRaster = snap_raster

    # remove data that is outside the bounding box and snap the image
    print("Clipping {0}".format(rastname))

    tempout = os.path.join(tempdir,tail)
    try:
        arcpy.Clip_management(rastname, snap_meta.rectangle, tempout, "#", "#", "NONE", "MAINTAIN_EXTENT")
    except:
        arcpy.Clip_management(rastname, snap_meta.rectangle, tempout, "#", "#", "NONE")

    # load the newly cliped raster, find the offsets
    raster, meta = to_numpy(tempout)
    xoffset      = int(round((meta.Xmin - snap_meta.Xmin)/meta.cellWidth,0))
    yoffset      = int(round((meta.Ymin - snap_meta.Ymin)/meta.cellHeight,0))

    # first iteration of clip with snap_raster environment sometimes has rounding issues
    # run clip a second time if raster does not fully lie within the extents of the bounding box
    if meta.Xsize > snap_meta.Xsize or meta.Ysize > snap_meta.Ysize:
        arcpy.Clip_management(tempout,snap_meta.rectangle, tempout[:-4] + '2.tif',"#","#","NONE")

        # reload and recalculate offsets
        raster, meta = to_numpy(tempout[:-4] + '2.tif')
        xoffset      = int(round((meta.Xmin - snap_meta.Xmin)/meta.cellWidth,0))
        yoffset      = int(round((meta.Ymin - snap_meta.Ymin)/meta.cellHeight,0))

    # plop the snapped raster into the new output raster, alter the metadata, and save it
    meta.Xmin   = snap_meta.Xmin
    meta.Ymin   = snap_meta.Ymin
    Yrange      = range(yoffset,(yoffset + meta.Ysize))
    Xrange      = range(xoffset,(xoffset + meta.Xsize))

    # create empty matrix of NoData_Values to store output
    print('Saving {0}'.format(rastname))
    newraster = numpy.zeros((snap_meta.Ysize, snap_meta.Xsize)) + float(meta.NoData_Value)

    print("recasting rastwer with shape ({1}) to shape ({0})".format(newraster.shape, raster.shape))

    '''print snap_meta.Ysize
    print meta.Ysize
    print yoffset

    print snap_meta.Xsize
    print meta.Xsize
    print xoffset'''

    newraster[(snap_meta.Ysize - meta.Ysize - yoffset):(snap_meta.Ysize - yoffset),
              (snap_meta.Xsize - meta.Xsize - xoffset):(snap_meta.Xsize - xoffset)] = raster[:,:]
    from_numpy(newraster, meta, outname, NoData_Value, numtype)

    # clean up
    shutil.rmtree(tempdir)
    return snap_meta, meta