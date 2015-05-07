# local imports
from dnppy import core

__all__=['spatially_match',     # appears defective
         'clip_and_snap',       # complete
         'clip_to_shape']       # complete


def spatially_match(snap_raster, rasterlist, outdir, numtype = False, NoData_Value = False,
                            resamp_type = False):
    """
    Prepares input rasters for further numerical processing
    
     This function simply ensures all rasters in "rasterlist" are identically projected
     and have the same cell size, then calls the raster.clip_and_snaps function to ensure
     that the cells are perfectly coincident and that the total spatial extents of the images
     are identical, even when NoData values are considered. This is usefull because it allows
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
    """

    # import modules and sanitize inputs
    tempdir = os.path.join(outdir,'temp')
    import shutil
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
        tempname    = os.path.join(tempdir,tail)

        if snap_meta.projection.projectionName != meta.projection.projectionName:
            print 'The files are not the same projection!'
            core.project(rastname, snap_raster, tempname, resamp_type, snap_raster)
            usetemp = True

        if round(float(snap_meta.cellHeight)/float(meta.cellHeight),5)!=1 and \
        round(float(snap_meta.cellWidth)/float(meta.cellWidth),5)!=1:

            if resamp_type:
                cell_size = "{0} {1}".format(snap_meta.cellHeight,snap_meta.cellWidth)
                arcpy.Resample_management(rastname, tempname, cell_size, resamp_type)
                usetemp = True
                
            else:
                raise Exception("images are NOT the same resolution! {0} vs {1} input a resample type!".format(
                    (snap_meta.cellHeight,snap_meta.cellWidth),(meta.cellHeight,meta.cellWidth)))
            
        # define an output name and run the Clip_ans_Snap_Raster function on formatted tifs.
        head,tail   = os.path.split(rastname)
        outname     = core.create_outname(outdir, rastname,'matched')

        # if a temporary file was created in previous steps, use that one for clip and snap               
        if usetemp:   
            clip_and_snap(snap_raster, tempname, outname, numtype, NoData_Value)
        else:
            clip_and_snap(snap_raster, rastname, outname, numtype, NoData_Value)
            
        print(' Finished matching raster!')

    shutil.rmtree(tempdir)
    return
           

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

    # plop the snaped raster into the new output raster, alter the metadata, and save it
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
    return snap_meta,meta


def clip_to_shape(rasterlist, shapefile, outdir = False):
    """
     Simple batch clipping script to clip rasters to shapefiles. 

     Inputs:
       rasterlist      single file, list of files, or directory for which to clip rasters
       shapefile       shapefile to which rasters will be clipped
       outdir          desired output directory. If no output directory is specified, the
                       new files will simply have '_c' added as a suffix. 
    """

    rasterlist = enf_rastlist(rasterlist)

    # ensure output directorycore.exists
    if outdir and not os.path.exists(outdir):
        os.makedirs(outdir)

    for raster in rasterlist:

        # create output filename with "c" suffix
        outname = core.create_outname(outdir,raster,'c')
        
        # perform double clip , first using clip_management (preserves no data values)
        # then using arcpy.sa module which can actually do clipping geometry unlike the management tool.
        arcpy.Clip_management(raster,"#",outname,shapefile,"ClippingGeometry")
        out = sa.ExtractByMask(outname,shapefile)
        out.save(outname)
        print("Clipped and saved: {0}".format(outname))
    
    return
