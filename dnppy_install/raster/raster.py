"""
======================================================================================
                                   dnppy.raster
======================================================================================
 This script is part of (dnppy) or "DEVELOP National Program py"
 It is maintained by the Geoinformatics YP class.

It contains functions for fairly routine manipulations of raster data.
Also see dnppy.calc for 
"""

__author__ = ["Jeffry Ely, jeff.ely.08@gmail.com",
              "Lauren Makely, lmakely09@gmail.com"]


__all__ =['to_numpy',           # complete
          'from_numpy',         # complete
          'stack',              # complete
          'temporal_fill',      # planned development
          'find_overlap',       # complete
          'spatially_match',    # complete
          'clip_and_snap',      # complete
          'clip_to_shape',      # complete
          'define_null',        # complete
          'set_range_null',     # complete
          'is_rast',            # complete
          'grab_info',          # working, but incomplete
          'identify']           # working, but incomplete


from dnppy import core
if core.check_module('numpy'): import numpy
import arcpy
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    from arcpy import sa,env
    arcpy.env.overwriteOutput = True

#======================================================================================
def to_numpy(Raster, num_type=False):

    """
    Wrapper for arcpy.RasterToNumpyArray with better metadata handling
    
     This is just a wraper for the RasterToNumPyArray function within arcpy, but it also
     extracts out all the spatial referencing information that will probably be needed
     to save the raster after desired manipulations have been performed.
     also see raster.from_numpy function in this module.

     inputs:
       Raster              Any raster suported by the arcpy.RasterToNumPyArray function
       num_type            must be a string equal to any of the types listed at the following
                           address [http://docs.scipy.org/doc/numpy/user/basics.types.html]
                           for example: 'uint8' or 'int32' or 'float32'
     outputs:
       numpy_rast          the numpy array version of the input raster
       Metadata            An object with the following attributes.
           .Xmin            the left edge
           .Ymin            the bottom edge
           .Xmax            the right edge
           .Ymax            the top edge
           .Xsize           the number of columns
           .Ysize           the number of rows
           .cellWidth       resolution in x direction
           .cellHeight      resolution in y direction
           .projection      the projection information to give the raster
           .NoData_Value    the numerical value which represents NoData in this raster

     Usage example:
       call this function with  " rast,Metadata = raster.to_numpy(Raster) "
       perform numpy manipulations as you please
       then save the array with " raster.from_numpy(rast,Metadata,output)   "
    """

    # create a metadata object and assign attributes to it
    class metadata:

        def __init__(Raster):

            self.Ysize, self.Xsize  = Raster.shape
            
            self.cellWidth      = arcpy.Describe(Raster).meanCellWidth
            self.cellHeight     = arcpy.Describe(Raster).meanCellHeight

            self.Xmin           = arcpy.Describe(Raster).Extent.XMin
            self.Ymin           = arcpy.Describe(Raster).Extent.YMin
            self.Xmax           = Xmin + (xs * cellWidth)
            self.Ymax           = Ymin + (ys * cellHeight)
            
            self.rectangle      = ' '.join([str(Xmin), str(Ymin), str(Xmax), str(Ymax)])
            self.projection     = arcpy.Describe(Raster).spatialReference
            self.NoData_Value   = arcpy.Describe(Raster).noDataValue
            return
        

    # read in the raster as an array
    if raster.is_rast(Raster):

        numpy_rast  = arcpy.RasterToNumPyArray(Raster)
        Metadata    = metadata(numpy_rast)
        
        if num_type:
            numpy_rast = numpy_rast.astype(num_type)
            
    else:  
        print("{raster.to_numpy} Raster '{0}'does not exist".format(Raster))

    return numpy_rast, Metadata



def from_numpy(numpy_rast, Metadata, outpath, NoData_Value = False, num_type = False):
    """
    Wrapper for arcpy.NumPyArrayToRaster function with better metadata handling
    
     this is just a wraper for the NumPyArrayToRaster function within arcpy. It is used in
     conjunction with raster.to_numpy to streamline reading image files in and out of numpy
     arrays. It also ensures that all spatial referencing and projection info is preserved
     between input and outputs of numpy manipulations.

     inputs:
       numpy_rast          the numpy array version of the input raster
       Metadata            The variable exactly as output from "raster.to_numpy"
       outpath             output filepath of the individual raster
       NoData_Value        the no data value of the output raster
       num_type            must be a string equal to any of the types listed at the following
                           address [http://docs.scipy.org/doc/numpy/user/basics.types.html]
                           for example: 'uint8' or 'int32' or 'float32'

     Usage example:
       call raster.to_numpy with  "rast,Metadata = raster.to_numpy(Raster)"
       perform numpy manipulations as you please
       then save the array with "raster.from_numpy(rast, Metadata, output)"
    """

    if num_type:
        numpy_rast = numpy_rast.astype(num_type)

    if not NoData_Value:
        NoData_Value = Metadata.NoData_Value
            
    llcorner= arcpy.Point(Metadata.Xmin,Metadata.Ymin)
    
    # save the output.
    OUT = arcpy.NumPyArrayToRaster(numpy_rast,llcorner,Metadata.cellWidth,Metadata.cellHeight)
    OUT.save(outpath)

    # define its projection
    try: arcpy.DefineProjection_management(outpath,Metadata.projection)
    except: pass

    # reset the NoData_Values
    try: arcpy.SetRasterProperties_management(outpath, data_type="#", nodata = "1 " + str(NoData_Value))
    except: pass
    
    # do statistics and pyramids
    arcpy.CalculateStatistics_management(outpath)
    arcpy.BuildPyramids_management(outpath)
    
    print("{raster.from_numpy} Saved output file as {0}".format(outpath))

    return



def is_rast(filename):
    """ Verifies that input filenamecore.exists, and is of raster format"""

    import os
    
    rast_types=['bil','bip','bmp','bsq','dat','gif','img','jpg','jp2','png','tif',
                'BIL','BIP','BMP','BSQ','DAT','GIF','IMG','JPG','JP2','PNG','TIF']
    ext = filename[-3:]

    if os.path.isfile(filename):
        for rast_type in rast_types:
            if ext == rast_type:
                return(True)

    return(False)


          
def stack(raster_paths):
    """
    Creates 3d numpy array from multiple coincident rasters
    
    This function is to create a 3d numpy array out of multiple coincident rasters.
    Usefull for layering multiple bands in a sceen or bulding a time series "data brick".
    It is important that all layers that are stacked are perfectly coincident, having
    identical pixel dimensions, resolution, projection, and spatial referencing. 

    Inputs:
        raster_paths    list of filepaths to rasters to be stacked. They will be stacked in
                        the same order as they ar einput

    Returns:
        stack           3d numpy array containing stacked raster data
        meta            metadata of the first raster layer. All layers should have identical
                        metadata.
    """
 
    for z,raster in enumerate(raster_paths):
        temp_image, temp_meta = raster.to_numpy(raster)

        if z==0:
            stack = numpy.zeros((len(raster_paths),temp_meta.Ysize,temp_meta.Xsize))
        
        stack[z,:,:] = temp_image
        meta = temp_meta
        print(vars(meta))
        
    return stack, meta



def find_overlap(file_A, NoData_A, file_B, NoData_B, outpath, Quiet=False):
    """
     Finds overlaping area between two raster images.
     
     this function examines two images and outputs a raster raster.identifying pixels where both
     rasters have non-NoData values. Output raster has 1's where both images have data and
     0's where one or both images are missing data.

     inputs:
       file_A      the first file
       NoData_A    the NoData value of file A
       file_B      the second file
       NoData_B    the NoData value of file B
       outpath     the output filename for the desired output. must end in ".tif"
    """
    
    # import modules
    if check_module('numpy'): import numpy
    if not raster.is_rast(file_A) or not raster.is_rast(file_B):
        print '{raster.find_overlap} both inputs must be rasters!'

    # spatially match the rasters
    print '{raster.find_overlap} preparing input rasters!'
    raster.clip_and_snap(file_A,file_B,file_B,False,NoData_B)
    
    # load the rasters as numpy arays.
    a,metaA = raster.to_numpy(file_A)
    b,metaB = raster.to_numpy(file_B)

    Workmatrix = numpy.zeros((metaA.Ysize,metaA.Xsize))
    Workmatrix = Workmatrix.astype('uint8')

    a[(a >= NoData_A*0.99999) & (a <= NoData_A*1.00001)] = int(1)
    b[(b >= NoData_B*0.99999) & (b <= NoData_B*1.00001)] = int(1)

    print '{raster.find_overlap} Finding overlaping pixels!'
    Workmatrix = a + b
    Workmatrix[Workmatrix <2] = int(0)
    Workmatrix[Workmatrix >2] = int(2)
                
    print '{raster.find_overlap} Saving overlap file!'          
    raster.from_numpy(Workmatrix, metaA, outpath,'0','uint8',False)
    Set_Null_Values(outpath,0,False)
    arcpy.RasterToPolygon_conversion(outpath, outpath[:-4]+'.shp', 'NO_SIMPLIFY')
    
    return metaA, metaB



def spatially_match(snap_raster, rasterlist, outdir, numtype=False, NoData_Value=False,
                            resamp_type=False, Quiet=False):
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
    
    rasterlist = core.enf_rastlist(rasterlist)
   core.exists(snap_raster)
    usetemp=False

    # set the snap raster environment in arcmap.
    arcpy.env.snapRaster=snap_raster

    print '{raster.spatially_match} Loading snap raster: ',snap_raster
    _,snap_meta = raster.to_numpy(snap_raster)
    print '{raster.spatially_match} Bounds of rectangle to define boundaries: [',snap_meta.rectangle,']'

    # for every raster in the raster list, snap rasters and clip.
    for rastname in rasterlist:
        
        _,meta = raster.to_numpy(rastname)
        head,tail=os.path.split(rastname)
        tempname=os.path.join(tempdir,tail)

        if snap_meta.projection.projectionName != meta.projection.projectionName:
            print '{raster.spatially_match} The files are not the same projection!'
            Project_Files(rastname,snap_raster,tempname,resamp_type,snap_raster)
            usetemp=True

        if round(float(snap_meta.cellHeight)/float(meta.cellHeight),5)!=1 and \
        round(float(snap_meta.cellWidth)/float(meta.cellWidth),5)!=1:

            if resamp_type:
                arcpy.Resample_management(rastname,tempname,snap_raster, resamp_type)
                usetemp=True
                
            print '{raster.spatially_match} The files are not the same resolution!'
            print '{raster.spatially_match} Resample the images manually or input a value for "resampe_type"!'

        # define an output name and run the Clip_ans_Snap_Raster function on formatted tifs.
        head,tail=os.path.split(rastname)
        outname=os.path.join(outdir,tail[:-4]+'_matched.tif')

        # if a temporary file was created in previous steps, use that one for clip and snap               
        if usetemp:   
            raster.clip_and_snap(snap_raster,tempname,outname,numtype,NoData_Value,False)
        else:
            raster.clip_and_snap(snap_raster,rastname,outname,numtype,NoData_Value,False)  
        print '{raster.spatially_match} Finished matching raster!'

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
       snap_meta       metadata of the snap_raster file as output by raster.to_numpy
       meta            metadata of the rastername file as output by raster.to_numpy
    """

    # grab metadata for rastname
    _,snap_meta = raster.to_numpy(snap_raster)
    _,meta      = raster.to_numpy(rastname)

    if not NoData_Value:
        NoData_Value = meta.NoData_Value

    if not numtype:
        numtype='float32'
        
    head,tail=os.path.split(outname)
    tempdir=os.path.join(head,'temp')
    if not os.path.isdir(tempdir):
        os.makedirs(tempdir)

    # set the snap raster environment in arcmap.
    arcpy.env.snapRaster=snap_raster

    # remove data that is outside the bounding box and snap the image
    print '{raster.clip_and_snap} Clipping '+rastname
    tempout=os.path.join(tempdir,tail)
    try:    arcpy.Clip_management(rastname,snap_meta.rectangle, tempout,"#","#","NONE","MAINTAIN_EXTENT")
    except: arcpy.Clip_management(rastname,snap_meta.rectangle, tempout,"#","#","NONE")
    
    # load the newly cliped raster, find the offsets
    raster,meta = raster.to_numpy(tempout)
    xoffset = int(round((meta.Xmin - snap_meta.Xmin)/meta.cellWidth,0))
    yoffset = int(round((meta.Ymin - snap_meta.Ymin)/meta.cellHeight,0))

    # first iteration of clip with snap_raster environment sometimes has rounding issues
    # run clip a second time if raster does not fully lie within the extents of the bounding box
    if meta.Xsize > snap_meta.Xsize or meta.Ysize > snap_meta.Ysize:
        arcpy.Clip_management(tempout,snap_meta.rectangle, tempout[:-4] + '2.tif',"#","#","NONE")

        # reload and recalculate offsets
        raster,meta = raster.to_numpy(tempout[:-4] + '2.tif')
        xoffset = int(round((meta.Xmin - snap_meta.Xmin)/meta.cellWidth,0))
        yoffset = int(round((meta.Ymin - snap_meta.Ymin)/meta.cellHeight,0))

    # plop the snaped raster into the new output raster, alter the metadata, and save it
    meta.Xmin = snap_meta.Xmin
    meta.Ymin = snap_meta.Ymin
    Yrange= range(yoffset,(yoffset + meta.Ysize))
    Xrange= range(xoffset,(xoffset + meta.Xsize))

    # create empty matrix of NoData_Values to store output
    print('{raster.clip_and_snap} Saving formated file' + rastname)
    newraster=numpy.zeros((snap_meta.Ysize,snap_meta.Xsize))+float(meta.NoData_Value)
    newraster[(snap_meta.Ysize - meta.Ysize - yoffset):(snap_meta.Ysize - yoffset),
              xoffset:(xoffset + meta.Xsize)] = raster[:,:]
    raster.from_numpy(newraster,meta,outname,NoData_Value,numtype,False)

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

    rasterlist=Enforce_Rasterlist(rasterlist)

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
        print("{raster.clip_to_shape} Clipped and saved: " + outname)

    print("{raster.clip_to_shape} Clipping complete! \n")
    
    return


def many_stats(rasterlist, low_thresh, high_thresh, outdir, NoData_Value, saves = ['AVG','NUM','STD']):
    """
    Take statitics across many input raster layers
    
     this function is used to take statistics on large groups of rasters with identical
     spatial extents. Similar to Rolling_Raster_Stats

     Inputs:
       rasterlist      list of rasters or directory of rasters on which to perform statistics
       low_thresh      values below low_thresh are assumed erroneous and set to NoData
       high_thresh     values above high_thresh are assumed erroneous and set to NoData.
       outdir          Directory where output should be stored.
       NoData_Value    Value representing NoData.
       saves           which statistics to save in a raster. Any of
                           AVG = rasters showing average value across all input rasters
                           NUM = rasters showing the number of good pixels which comprised AVG
                           STD = rasters showing the standard deviation of pixels
                       Defaults to all three ['AVG','NUM','STD'].
    """
    
    print('This function will eventually be developed')
    print('if you need it ASAP, contact the geoinformatics YPs!')
    
    return    



def define_null(filelist, NoData_Value, Quiet=False):
    """
    Simple batch NoData setting function. Makes raster data more arcmap viewing friendly
    
     Function inputs a list of raster (usually tifs) files and sets no data values. This
     function does not actually change the raster values in any way, and simply defines which
     numerical values to be considered NoData in metadata.

     inputs:
       filelist        list of files for which to set NoData values. easily created with
                       "core.list_files" function
       NoData_Value    Value to declare as NoData (usually 0 or -9999)
       Quiet           Set Quiet to 'True' if you don't want anything printed to screen.
                       Defaults to 'False' if left blank.
    """

    filelist = core.enf_rastlist(filelist)

    # iterate through each file in the filelist and set nodata values
    for filename in filelist:

        arcpy.SetRasterProperties_management(filename,data_type="#",statistics="#",
                    stats_file="#",nodata="1 "+str(NoData_Value))
        if not Quiet:
            print '{raster.define_null} Set NoData values in ' + filename
               
    if not Quiet:print '{raster.define_null} Finished! \n'            
    return



def set_range_null(filelist,above,below,NoData_Value,Quiet=False):
    """
    Changes values within a certain range to NoData
    
     similar to raster.define_null, but can take an entire range of values to set to NoData.
     useful in filtering obviously erroneous high or low values from a raster dataset.

     inputs:
       filelist    list of files for which to set NoData values. easily created with
                       "core.list_files" function
       above       will set all values above this, but below "below" to NoData
                       set to 'False' if now upper bound exists
       below       will set all values below this, but above "above" to NoData
                       set to 'False' if no lower bound exists
       Quiet       Set Quiet to 'True' if you don't want anything printed to screen.
                       Defaults to 'False' if left blank.
    """

    # sanitize filelist input
    filelist=Enforce_Rasterlist(filelist)

    # iterate through each file in the filelist and set nodata values
    for filename in filelist:
        #load raster as numpy array and save spatial referencing.
        raster, meta = raster.to_numpy(filename)

        if above and below:
            raster[raster <= below and raster >= above] = NoData_Value
        elif above:
            raster[raster >= above] = NoData_Value
        elif below:
            raster[raster <= below] = NoData_Value
            
        raster.from_numpy(raster, meta, filename)
        arcpy.SetRasterProperties_management(filename,data_type="#",statistics="#",
                    stats_file="#",nodata="1 "+str(NoData_Value))
        
        if not Quiet:
            print '{raster.set_range_null} Set NoData values in ' + filename

    if not Quiet:print '{raster.set_range_null} Finished!'            
    return


          
def rolling_stats(centers, windows, window_width, low_thresh, high_thresh, outdir,
                    NoData_Value, chunks=False, start_chunk=False, saves = ['AVG','NUM','STD']):
    """
    Takes rolling statistics on time series raster data.

     Similar to "raster.many_stats" but with optimization for statistics across many
     partially overlapping datasets and the ability to handle extremely large datasets.

     this function was built specifically for the Langley Northwest Agriculture team in
     Fall of 2014. It was designed to perform statistics on many raster blocks as output from
     the 'core.rolling_window' function, therefore its inputs include centers, windows, and window width.

     the function was used to take moving averages of MODIS land surface temperature data
     where efficiency could be gained by keeping data loaded for one window in memory for
     the next window, since 80% or more of each window overlaps with the previous one. This
     very significantly reduced processing time, but required chunking data to avoid hitting
     pythons 2GB memory limit (32 bit version).

     Inputs:
       centers         Array of filenames representing the center of each list in "windows".
       windows         2d array of filenames. window groupings as output from "core.rolling_window".
       window_width    Window width used to generate the windows in 2d array "windows" used
                       for naming.
       low_thresh      values below low_thresh are assumed erroneous and set to NoData.
       high_thresh     values above high_thresh are assumed erroneous and set to NoData.
       outdir          Directory where output should be stored.
       NoData_Value    Value representing NoData.
       chunks          The number of chunks to split processing into. Chunks are vertical
                       slices. leave blank or False to allow automatic determination of a
                       safe chunk value to limit matrix size to 3 million values at once.
       start_chunk     Value of chunk to start at. Used to get around the memory leak bug.
       saves           which statistics to save in a raster. Any of
                           AVG = rasters showing average value across all input rasters
                           NUM = rasters showing the number of good pixels which comprised AVG
                           STD = rasters showing the standard deviation of pixels
                       Defaults to all three ['AVG','NUM','STD'].

     Bugs:
       Some memory leaking appears to occur, this problem has not been solved, but using
       a 64 bit installation of python has been found to help by increasing memory headroom.
       If a memory error occurs when processing large datasets, users can input a value for
       "start_chunk" equal to the value of the active chunk at the time of error. This will
       allow memory to clear and pick up at the beginning of the chunk where the crash occurred.
    """

    saves = core.enf_list(saves)
    
    #creates output directory if not already there
    if not os.path.exists(outdir): os.makedirs(outdir)
    tempdir=os.path.join(outdir,'Chunks')
    if not os.path.exists(tempdir):os.makedirs(tempdir)

    #set up empty tracking lists
    chunk_average_list =[]
    chunk_count_list =[]
    chunk_std_list=[]
    ychunks=[]
    chunk_name_list=[]   
    
    # define sizes based on window size and dims of first image in window
    temp,meta=raster.to_numpy(windows[0][0])
    xs,ys=temp.shape
    zs=len(windows[0])
    xyzs=xs*ys*zs

    # automatically determine number of chunks to use by limiting the size of
    # any given data brick to 3 million values
    if not chunks: chunks=xyzs/3000000+1

    # find the dimensions of the chunks for subprocessing of the data
    # data is split into chunks to avoid hitting memory limits. (2GB for 32 bit python)
    for sub in range(chunks):
        ychunks.append(range(((sub)*ys)/chunks,(((sub+1)*ys)/chunks)))
        chunk_name_list.append('Chnk'+str(sub))

    # find the maximum width of a chunk    
    width=len(max(ychunks,key=len))
    
    print('{Rolling_Raster_Stats} Split data into ' + str(chunks) + ' chunks.')

    # process each chunk
    for chunkID,ychunk in enumerate(ychunks):
        if chunkID>=start_chunk:
            
            print '{Rolling_Raster_Stats}  Processing chunk number '+ str(chunkID) + ' with width '+ str(width)
            
            for j,window in enumerate(windows):
                filtered=0
                center=centers[j]
                print '{Rolling_Raster_Stats}  Window center : ' + center
                info=core.Grab_Data_Info(center,False,True)
                
                # Create_output_filenames based on the file representing the window center
                head,tail = os.path.split(center)
                chunk_average_name= os.path.join(tempdir,'.'.join(tail.split('.')[:-1])+
                    '_W'+str(window_width).zfill(2)+'_C'+info.year+info.j_day+'_Avg_Chnk'+str(chunkID)+'.tif')
                chunk_count_name= os.path.join(tempdir,'.'.join(tail.split('.')[:-1])+
                    '_W'+str(window_width).zfill(2)+'_C'+info.year+info.j_day+'_Num_Chnk'+str(chunkID)+'.tif')
                chunk_std_name= os.path.join(tempdir,'.'.join(tail.split('.')[:-1])+
                    '_W'+str(window_width).zfill(2)+'_C'+info.year+info.j_day+'_Std_Chnk'+str(chunkID)+'.tif')

                # clear existing rollover list and create a new one
                rollover_from=[]
                rollover_to=[]

                # if this is the first window we've examined, create empty numpy matrix
                # based on dimensions of the first file, and number of entries in the first window
                if j==0:
                    newmatrix = numpy.zeros((xs,width,len(window)))
                    oldmatrix = numpy.zeros((xs,width,len(window)))
                    newcount  = numpy.zeros((xs,width,len(window)))
                    oldcount  = numpy.zeros((xs,width,len(window)))
                    
                # if this is not the first window, check to see if any of the current files
                # were in the previous window
                elif j>0:
                    for filename in windows[j]:
                        if filename in windows[j-1]:
                            # track rollover locations, to and from, for shuffling data between windows
                            rollover_from.append(windows[j-1].index(filename))
                            rollover_to.append(windows[j].index(filename))
                            
                # for all files in the group, populate the newmatrix
                for i,item in enumerate(window):
                    path,name=os.path.split(item)
                    if i in rollover_to:
                        index=rollover_to.index(i)
                        newmatrix[:,:,i]=oldmatrix[:,:,rollover_from[index]]
                    else:
                        print '{Rolling_Raster_Stats} New file loaded: '+ name
                        tempmatrix,x,y,w,h,spat_ref = raster.to_numpy(Raster)
                        try:
                            newmatrix[:,range(len(ychunk)),i]=tempmatrix[:,ychunk]
                            newmatrix[:,range(len(ychunk),width),i]=numpy.zeros((xs,width-len(ychunk)))+NoData_Value
                        except:
                            print 'Abnormal Image discovered! filling with nodata!'
                            newmatrix[:,range(width),i]=numpy.zeros((xs,width))+NoData_Value
                
                # examine each pixel, add pixels with good data to the count.
                print '{Rolling_Raster_Stats} Filtering bad values and calculating statistics!'

                # start by looking at layers. Skip layers which were rolled over and already processed
                for z in range(zs):

                    # only perform this data filtering if it hasn't already been done on this "z slice"
                    if not z in rollover_to:
                        for x in range(xs):
                            for y in range(width):

                                # if a pixel value is not 0 (NoData), add to the count
                                if not round(newmatrix[x,y,z]/NoData_Value,10)==1:
                                    newcount[x,y,z] = 1

                                    # filter data for potential errors
                                    # by threshold values
                                    if high_thresh and newmatrix[x,y,z]>=high_thresh:
                                        newmatrix[x,y,z]=NoData_Value
                                        filtered +=1
                                        newcount[x,y,z]= 0
                                        
                                    if low_thresh and newmatrix[x,y,z]<=low_thresh:
                                        newmatrix[x,y,z]=NoData_Value
                                        filtered +=1
                                        newcount[x,y,z]= 0
                                    
                    else: newcount[:,:,z]=oldcount[:,:,z]

                # total up all z-wise entries in the count matrix.
                del count
                count=numpy.sum(newcount,axis=2)
                
                # perform per-pixel data filtering by pulling out values greater than 3
                # standard deviations away from the mean value for that pixel.
                
                Std = numpy.zeros((xs,width))
                average = numpy.zeros((xs,width))
                
                for x in range(xs):
                    for y in range(width):
                        
                        # perform initial filtering of edge values.
                        pixels=newmatrix[x,y,:][newmatrix[x,y,:] !=NoData_Value]

                        if len(pixels)>=3:
                            pixel_avg=numpy.mean(pixels)
                            pixel_std=numpy.std(pixels)
                            high_tail=float(pixel_avg+3*pixel_std)
                            low_tail=float(pixel_avg-3*pixel_std)

                            for z,pixel in enumerate(pixels):
                                if pixel>=high_tail or pixel<=low_tail:
                                    pixels[z]=NoData_Value
                                    filtered   += 1
                                    count[x,y] -= 1

                        # perform the statistics now that outliers are removed           
                        pixels=pixels[pixels !=NoData_Value]

                        if len(pixels)>=3:
                            Std[x,y]= numpy.std(pixels)   
                            average[x,y]= numpy.mean(pixels)   
                        elif len(pixels)>=1:
                            average[x,y]= numpy.mean(pixels)
                            Std[x,y] = NoData_Value
                        else:
                            average[x,y]=NoData_Value
                            Std[x,y]=NoData_Value
                        del pixels
                                
                print '{Rolling_Raster_Stats}  filtered '+ str(filtered) + ' total pixel values'

                #write output to chunk file

                if 'AVG' in saves: 
                    raster.to_numpy(average,x,y,w,h,spat_ref,chunk_average_name)
                    chunk_average_list.append(chunk_average_name)
                    
                if 'NUM' in saves:
                    raster.to_numpy(count,x,y,w,h,spat_ref,chunk_average_name)
                    chunk_count_list.append(chunk_count_name)
                    
                if 'STD' in saves:
                    raster.to_numpy(Std,x,y,w,h,spat_ref,chunk_average_name)
                    chunk_std_list.append(chunk_std_name)

                # clean up at the end of each window and set the newmatrix to the old one
                del rollover_from[:]
                del rollover_to[:]
                del Std
                del average
                
                oldmatrix=newmatrix
                oldcount=newcount

#.......................................................................................
    print 'Finished processing chunks! Stitching them back together!'
    # at the end of each chunk processing, begin rejoining the output slices
    out_Avg = numpy.zeros((xs,ys))
    out_Num = numpy.zeros((xs,ys))
    out_Std = numpy.zeros((xs,ys))

    # assemble all chunks
    for centerID,center in enumerate(centers):
        print center

        # Create_output_filenames of completely assembled chunks.
        head,tail = os.path.split(center)
        info=core.Grab_Data_Info(center,False,True)
        average_name= os.path.join(outdir,'.'.join(tail.split('.')[:-1])+
            '_W'+str(window_width).zfill(2)+'_C'+info.year+info.j_day+'_Avg.tif')
        count_name= os.path.join(outdir,'.'.join(tail.split('.')[:-1])+
            '_W'+str(window_width).zfill(2)+'_C'+info.year+info.j_day+'_Num.tif')
        std_name= os.path.join(outdir,'.'.join(tail.split('.')[:-1])+
            '_W'+str(window_width).zfill(2)+'_Ce'+info.year+info.j_day+'_Std.tif')

         # look for these filenames and fill in the final output matrices
        if 'AVG' in saves:
            for chunkID,ychunk in enumerate(ychunks):
                Avg_chunk= os.path.join(tempdir,'.'.join(tail.split('.')[:-1])+
                    '_W'+str(window_width).zfill(2)+'_C'+info.year+info.j_day+'_Avg_Chnk'+str(chunkID)+'.tif')       

                temp,x,y,w,h,spat_ref = raster.to_numpy(Avg_chunk)
                out_Avg[:,ychunk]=temp[:,range(len(ychunk))]
                
            raster.from_numpy(out_Avg,x,y,w,h,spat_ref,average_name)
            
        if 'NUM' in saves:
            for chunkID,ychunk in enumerate(ychunks):
                Num_chunk= os.path.join(tempdir,'.'.join(tail.split('.')[:-1])+
                    '_W'+str(window_width).zfill(2)+'_C'+info.year+info.j_day+'_Num_Chnk'+str(chunkID)+'.tif')      

                temp,x,y,w,h,spat_ref = raster.to_numpy(Num_chunk)
                out_Num[:,ychunk]=temp[:,range(len(ychunk))]
            
            raster.from_numpy(out_Num,x,y,w,h,spat_ref,count_name)
            
        if 'STD' in saves:
            for chunkID,ychunk in enumerate(ychunks):
                Std_chunk= os.path.join(tempdir,'.'.join(tail.split('.')[:-1])+
                    '_W'+str(window_width).zfill(2)+'_C'+info.year+info.j_day+'_Std_Chnk'+str(chunkID)+'.tif')       
                
                temp,x,y,w,h,spat_ref = raster.to_numpy(Std_chunk)
                out_Std[:,ychunk]=temp[:,range(len(ychunk))]

            raster.from_numpy(out_Std,x,y,w,h,spat_ref,std_name)
            
    print '{Rolling_Raster_Stats} Finished with all processing!'
    
    return



def temporal_fill(filelist,Quiet=False):

    """
     This function is designed to input a time sequence of rasters with partial voids and
     output a copy of each input image with every pixel equal to the last good value taken.
     This function will step forward in time through each raster and fill voids from the values
     of previous rasters. The resulting output image will contain all the data that was in the
     original image, with the voids filled with older data. A second output image will be
     generated where the pixel values are equal to the age of each pixel in the image. So
     if a void was filled with data thats 5 days old, the "age" raster will have a value of
     "5" at that location.
    """

    print 'This function will eventually be developed' 
    print 'if you need it ASAP, contact the geoinformatics Fellows!'
    
    return



def grab_info(filepath, data_type = False, CustGroupings = False):

    """
    Extracts in-filename metadata from common NASA data products

     This function simply extracts relevant sorting information from a MODIS or Landsat
     filepath of any type or product and returns object properties relevant to that data.
     it will be expanded to include additional data products in the future.

     Inputs:
           filepath        Full or partial filepath to any modis product tile
           data_type       Manually tell the software what the data is.
           CustGroupings   User defined sorting by julian days of specified bin widths.
                           input of 5 for example will group January 1,2,3,4,5 in the first bin
                           and january 6,7,8,9,10 in the second bin, etc.

     Outputs:
           info            on object containing the attributes (product, year, day, tile)
                           retrieve these values by calling "info.product", "info.year" etc.

     Attributes by data type:
           All             type,year,j_day,month,day,season,CustGroupings,suffix

           MODIS           product,tile
           Landsat         sensor,satellite,WRSpath,WRSrow,groundstationID,Version,band

     Attribute descriptions:
           type            NASA data type, for exmaple 'MODIS' and 'Landsat'
           year            four digit year the data was taken
           j_day           julian day 1 to 365 or 366 for leap years
           month           three character month abbreviation
           day             day of the month
           season          'Winter','Spring','Summer', or 'Autumn'
           CustGroupings   bin number of data according to custom group value. sorted by
                           julian day
           suffix          Any additional trailing information in the filename. used to find
                           details about special

           product         usually a level 3 data product from sensor such as MOD11A1
           tile            MODIS sinusoidal tile h##v## format

           sensor          Landsat sensor
           satellite       usually 5,7, or 8 for the landsat satellite
           WRSpath         Landsat path designator
           WRSrow          Landsat row designator
           groundstationID ground station which recieved the data download fromt he satellite
           Version         Version of landsat data product
           band            band of landsat data product, usually 1 through 10 or 11.
    """

    
    # pull the filename and path apart 
    path,name = os.path.split(filepath)
    
    # create an info object class instance
    class info_object(object):pass
    info = info_object()

    # figure out what kind of data these files are. 
    if not data_type:
        data_type = identify(name)

    if data_type == 'MODIS':
        params  =['product','year','j_day','tile','type','version','tag','suffix']
        n       = name.split('.')
        end     = n[4]
        string  =[n[0],name[9:13],name[13:16],n[2],'MODIS',n[3],end[:13],end[13:]]

    if data_type == 'MODIS':
        params  =['product','year','j_day','tile','type','version','tag','suffix']
        n       = name.split('.')
        end     = n[4]
        string  =[n[0],name[9:13],name[13:16],n[2],'MODIS',n[3],end[:13],end[13:]]
            
    elif data_type =='Landsat':
        params  =['sensor','satellite','WRSpath','WRSrow','year','j_day','groundstationID',
                                                        'Version','band','type','suffix']
        n       = name.split('.')[0]
        string  =[n[1],n[2],n[3:6],n[6:9],n[9:13],n[13:16],n[16:19],
                n[19:21],n[23:].split('_')[0],'Landsat','_'.join(n[23:].split('_')[1:])]
            
    elif data_type == 'WELD_CONUS' or data_type == 'WELD_AK':
        params  = ['coverage','period','year','tile','start_day','end_day','type']
        n       = name.split('.')
        string  =[n[0],n[1],n[2],n[3],n[4][4:6],n[4][8:11],'WELD']
        # take everything after the first underscore as a suffix if onecore.exists.
        if '_' in name:
            params.append('suffix')
            string.append('_'.join(name.split('_')[1:]))
            
    elif data_type == 'ASTER':
        params  = ['product','N','W','type','period']
        n       = name.split('_')
        string  = [n[0],n[1][1:3],n[1][5:9],n[-1].split('.')[0],'none']
    
    elif data_type == 'TRMM':
        print '{Grab_Data_Info} no support for TRMM data yet! you could add it!'
        return(False)

    elif data_type == 'AMSR_E':
        print '{Grab_Data_Info} no support for AMSR_E data yet! you could add it!'
        return(False)

    elif data_type == 'AIRS':
        print '{Grab_Data_Info} no support for AIRS data yet! you could add it!'
        return(False)

    # if data doesnt look like anything!
    else:
        print 'Data type for file ['+name+'] could not be identified as any supported type'
        print 'improve this function by adding info for this datatype!'
        return(False)

    # Create atributes and assign parameter names and values
    for i in range(len(params)):
        setattr(info,params[i],string[i])
    
    # ................................................................................
    # perform additional data gathering only if data has no info.period atribute. Images with
    # this attribute represent data that is produced from many dates, not just one day.
    if not hasattr(info,'period'):
    # fill in date format values and custom grouping and season information based on julian day
    # many files are named according to julian day. we want the date info for these files.
        try:
            tempinfo    = datetime.datetime(int(info.year),1,1)+datetime.timedelta(int(int(info.j_day)-1))
            info.month  = tempinfo.strftime('%b')
            info.day    = tempinfo.day
            
        # some files are named according to date. we want the julian day info for these files
        except:
            fmt         = '%Y.%m.%d'
            tempinfo    = datetime.datetime.strptime('.'.join([info.year,info.month,info.day]),fmt)
            info.j_day  = tempinfo.strftime('%j')

    # fill in the seasons by checking the value of julian day
        if int(info.j_day) <=78 or int(info.j_day) >=355:
            info.season='Winter'
        elif int(info.j_day) <=171:
            info.season='Spring'
        elif int(info.j_day)<=265:
            info.season='Summer'
        elif int(info.j_day)<=354:
            info.season='Autumn'
        
    # bin by julian day if integer group width was input
    if CustGroupings:
        CustGroupings=core.enf_list(CustGroupings)
        for grouping in CustGroupings:
            if type(grouping)==int:
                groupname='custom' + str(grouping)
                setattr(info,groupname,1+(int(info.j_day)-1)/(grouping))
            else:
                print('{Grab_Data_Info} invalid custom grouping entered!')
                print('{Grab_Data_Info} [CustGrouping] must be one or more integers in a list')

    # make sure the filepath input actually leads to a real file, then give user the info
    if core.exists(filepath):
        if not Quiet:
            print '{Grab_Data_Info} '+ info.type + ' File ['+ name +'] has attributes '
            print vars(info)
        return(info)
    else:
        return(False)



def identify(name):

    """
    Compare filename against known NASA data file naming conventions to raster.identify it

     Nested within the raster.grab_info function

     Inputs:
       name        any filename of a file which is suspected to be a satellite data product

     Outputs:
       data_type   If the file is found to be of a specific data type, output a string
                   designating that type. The options are as follows, with urls for reference                          

     data_types:
           MODIS       https://lpdaac.usgs.gov/products/modis_products_table/modis_overview
           Landsat     http://landsat.usgs.gov/naming_conventions_scene_identifiers.php
           TRMM        http://disc.sci.gsfc.nasa.gov/precipitation/documentation/TRMM_README/
           AMSR_E      http://nsidc.org/data/docs/daac/ae_ocean_products.gd.html
           ASTER       http://mapaspects.org/article/matching-aster-granule-id-filenames
           AIRS        http://csyotc.cira.colostate.edu/documentation/AIRS/AIRS_V5_Data_Product_Description.pdf
           False       if no other types appear to be correct.
    """

    if  any( x==name[0:2] for x in ['LC','LO','LT','LE','LM']):
        return('Landsat')
    elif any( x==name[0:3] for x in ['MCD','MOD','MYD']):
        return('MODIS')
    elif any( x==name[0:4] for x in ['3A11','3A12','3A25','3A26','3B31','3A46','3B42','3B43']):
        return('TRMM')
    elif name[0:5]=='CONUS':
        return('WELD_CONUS')
    elif name[0:6]=='Alaska':
        return('WELD_AK')
    elif name[0:6]=='AMSR_E':
        return('AMSR_E')
    elif name[0:3]=='AST':
        return('ASTER')
    elif name[0:3]=='AIR':
        return('AIRS')

    
    else:
        return(False)


