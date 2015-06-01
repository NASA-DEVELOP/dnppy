__author__ = 'jwely'

from to_numpy import to_numpy
from from_numpy import from_numpy

import os
import arcpy
import shutil

def clip_and_snap(snap_raster, rastname, outname, NoData_Value = None):
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
       rastname        name of raster which should be snapped to the snap_raster
       NoData_Value    Value desired to represent NoData in the saved image.

     outputs:
       snap_meta       metadata of the snap_raster file as output by to_numpy
       meta            metadata of the rastername file as output by to_numpy
    """

    # grab metadata for rastname
    _,snap_meta = to_numpy(snap_raster)
    _,meta      = to_numpy(rastname)

    if NoData_Value is None:
        NoData_Value = meta.NoData_Value

    head, tail   = os.path.split(outname)
    tempdir     = os.path.join(head, 'temp')

    if not os.path.isdir(tempdir):
        os.makedirs(tempdir)

    # set the snap raster environment in arcmap
    arcpy.env.snapRaster = snap_raster

    # remove data that is outside the bounding box and snap the image
    print("Clipping {0}".format(rastname))

    tempout = os.path.join(tempdir,'tempclip.tif')
    try:
        arcpy.Clip_management(rastname, snap_meta.rectangle, tempout, "#", "#", "NONE", "MAINTAIN_EXTENT")
    except:
        arcpy.Clip_management(rastname, snap_meta.rectangle, tempout, "#", "#", "NONE")

    # load the newly clipped raster, find any residual offsets (usually a single pixel or two)
    raster, meta = to_numpy(tempout)
    xloff   = int(round((meta.Xmin - snap_meta.Xmin)/meta.cellWidth,0))
    yloff   = int(round((meta.Ymin - snap_meta.Ymin)/meta.cellHeight,0))
    xhoff   = int(round((meta.Xmax - snap_meta.Xmax)/meta.cellWidth,0))
    yhoff   = int(round((meta.Ymax - snap_meta.Ymax)/meta.cellHeight,0))

    # plop the snapped raster into the new output raster, alter the metadata, and save it
    meta.Xmin   = snap_meta.Xmin
    meta.Ymin   = snap_meta.Ymin
    meta.Xmax   = snap_meta.Xmax
    meta.Ymax   = snap_meta.Ymax

    newraster = raster[(-yloff) : (meta.Ysize - yhoff), (-xloff) : (meta.Xsize - xhoff)]

    from_numpy(newraster, meta, outname, NoData_Value)

    try:
        shutil.rmtree(tempdir)
    except: pass

    return snap_meta, meta