__author__ = 'jwely'


from dnppy import core
from to_numpy import to_numpy
from enf_rastlist import enf_rastlist
from clip_and_snap import clip_and_snap
from project_resample import project_resample

import os
import arcpy

def spatially_match(snap_raster, rasterlist, outdir,
                    NoData_Value = False, resamp_type = False):
    """
    Prepares input rasters for further numerical processing

     This function simply ensures all rasters in "rasterlist" are identically projected
     and have the same cell size, then calls the raster.clip_and_snap function to ensure
     that the cells are perfectly coincident and that the total spatial extents of the images
     are identical, even when NoData values are considered. This is useful because it allows
     the two images to be passed on for numerical processing as nothing more than matrices
     of values, and the user can be sure that any index in any matrix is exactly coincident
     with the same index in any other matrix. This is especially important to use when
     comparing different datasets from different sources outside arcmap, for example MODIS
     and Landsat data with an ASTER DEM.

     inputs:
       snap_raster     raster to which all other images will be snapped
       rasterlist      list of rasters, a single raster, or a directory full of tiffs which
                       will be clipped to the extent of "snap_raster" and aligned such that
                       the cells are perfectly coincident.
       outdir          the output directory to save newly created spatially matched tifs.
       resamp_type     The resampling type to use if images are not identical cell sizes.
                           "NEAREST","BILINEAR",and "CUBIC" are the most common.

    this function automatically invokes
        clip_and_snap
        project_resample
    """

    # import modules and sanitize inputs
    tempdir = os.path.join(outdir, 'temp')

    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    if not os.path.isdir(tempdir):
        os.makedirs(tempdir)

    rasterlist = enf_rastlist(rasterlist)
    core.exists(snap_raster)

    usetemp = False

    # set the snap raster environment in arcmap.
    arcpy.env.snapRaster = snap_raster

    print('Loading snap raster {0}'.format(snap_raster))
    _,snap_meta = to_numpy(snap_raster)
    print('Bounds of rectangle to define boundaries: [{0}]'.format(snap_meta.rectangle))

    # for every raster in the raster list, snap rasters and clip.
    for rastname in rasterlist:

        _,meta      = to_numpy(rastname)
        head,tail   = os.path.split(rastname)

        if snap_meta.projection.projectionName != meta.projection.projectionName:
            print('Projection discrepancy found. Reprojecting...')
            project_resample(rastname, snap_raster, tempdir, resamp_type)
            tempname    = core.create_outname(tempdir,tail,"p")
            usetemp     = True

        # define an output name and run the Clip_ans_Snap_Raster function on formatted tifs
        outname      = core.create_outname(outdir, rastname, "sm")

        # if a temporary file was created in previous steps, use that one for clip and snap
        if usetemp:
            clip_and_snap(snap_raster, tempname, outname, NoData_Value)
        else:
            clip_and_snap(snap_raster, rastname, outname, NoData_Value)

        print('Finished matching raster {0}'.format(rastname))

    return
