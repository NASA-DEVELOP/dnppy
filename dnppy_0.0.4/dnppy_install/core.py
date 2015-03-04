"""
======================================================================================
                                   dnppy.core
======================================================================================
 This script is part of (dnppy) or "DEVELOP National Program py"
 It is maintained by the Geoinformatics YP class.

 It is intended to accompany tutorials to get new programmers quickly up to speed
 and to serve as a singular source of usuful functions of sufficient quality.
 Use of these functions wherever possible could save you time, help make your code more
 robust, and increase its utility to future teams. If you wish to add new functions
 or modify existing ones, coordinate with the geoinformatics team.

 To use this module, just run the install script titled setup_dnppy.py
 You must already have python installed and be running on a windows machine.

 Requirements:
   Python 2.7
   Arcmap 10.2 or newer for some functions

   Example:
   from dnppy import core
   core.Sample_Function('test',False)
"""

#--------------------------------------------------------------------------------------
#           function name               development notes
#--------------------------------------------------------------------------------------
__all__=['Sample_Function',             # complete
         'Stack_Rasters',               # complete
         'Apply_Linear_Correction',     # active development
         'Temporal_Data_Fill',          # planned development
         'Find_Overlap',                # complete
         'Spatially_Match_Rasters',     # complete
         'Clip_and_Snap_Raster',        # complete
         'Clip_Rasters_to_Shape',       # complete
         'Many_Raster_Stats',           # planned development
         'Rolling_Raster_Stats',        # working with bugs
         'Raster_to_Numpy',             # complete
         'Numpy_to_Raster',             # complete
         'Calc_Degree_Days',            # complete
         'Calc_Daily_Chill_Hours',      # planned development
         'Accum_Degree_Days',           # complete
         'Resample_List',               # active development
         'Grab_Data_Info',              # working but incomplete
         'Project_Filelist',            # complete
         'Rolling_Window',              # complete
         'Files_in_Window',             # complete
         'Set_Null_Values',             # complete
         'Set_Range_to_Null',           # complete
         'Remove_Empty_folders',        # complete
         'Rename',                      # complete
         'Enforce_List',                # complete
         'Enforce_Filelist',            # complete
         'Enforce_Rasterlist',          # complete
         'List_Files',                  # complete
         'Identify',                    # complete
         'Move_file',                   # complete
         'Exists',                      # complete
         'IsRaster',                    # complete
         'Create_Outname',              # complete
         'Date_to_Julian',              # complete
         'Julian_to_Date',              # complete
         'check_module']                # complete

#--------------------------------------------------------------------------------------
# attempt to import most commonly used modules
import os, datetime, sys, glob, shutil, gc

# attempt to import all the common arcpy modules and settings
import arcpy
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    from arcpy import sa,env
    arcpy.env.overwriteOutput = True
#--------------------------------------------------------------------------------------
#=========================================================================================
def Sample_Function(inputs, Quiet=False):

    """
    this is an example docstring for our sample function

    This is where additional information goes like inputs/outputs/authors
    """

    outputs=inputs
    if not Quiet:
        print('This is a sample function!')
        print('try changing your statement to core.Sample_Function(str,True)')

    return(outputs)

#=========================================================================================
def Stack_Rasters(raster_paths):

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
        temp_image, temp_meta = Raster_to_Numpy(raster)

        if z==0:
            stack = numpy.zeros((len(raster_paths),temp_meta.Ysize,temp_meta.Xsize))
        
        stack[z,:,:] = temp_image
        meta = temp_meta
        print(vars(meta))
        
    return stack, meta

#=========================================================================================
def Apply_Linear_Correction(rasterlist, factor, offset, suffix='lc', outdir=False,
                                            save=True, floor = -999999, Quiet=False):

    """
    Applies a linear correction to a raster dataset.
    
     New offset rasters are saved in the output directory with a suffix of "lc"
     unless one is specified. This may be used to apply any kind of linear relationship
     that can be described with "mx + b" such as conversion between between K,C, and F.
     Also usefull when ground truthing satellite data and discovering linear errors.
     All outputs are 32 bit floating point values.

     Inputs:
       rastelrist      list of rasters, a single raster, or a directory full of tiffs to
                       Have a linear correction applied to them.
       factor          every pixel in the raster will be MULTIPLIED by this value. 
       offset          this offset value will be ADDED to every pixel in the raster.
       suffix          output files will take the same name as input files with this string
                       appended to the end. So input "FILE.tif" outputs "FILE_suffix.tif"
       floor           Used to manage NoData. All values less than floor are set to floor
                       then floor is set to the new NoData value. defaults to -999,999
       outdir          directory to save output rasters. "False" will save output images
                       in the same folder as the input images.
       save            If you do NOT wish to save the data, and only return a numpy
                       array and metadata of the image, set to "False"

     Returns:
       image           numpy array (matrix) of the linearly corrected data
       metadata        coresponding metadata to the image
       
     Example Usage:
           to convert from MODIS Land surface temperature from digital number to kelvin, you
           must simply multiply by 0.02 as the stated scale factor listed at the link below
           [https://lpdaac.usgs.gov/products/modis_products_table/myd11a1].

           Now that it is in kelvin, converting to Celcius can be done by adding (-273.15)
           So, use this function with
               factor = 0.02
               offset = -273.15
           and one may convert MODIS land surface temperature digital numbers directly to
           celcius!
     """
    
    if outdir and not os.path.isdir(outdir):
        os.makedirs(outdir)
    rasterlist = Enforce_Rasterlist(rasterlist)

    for raster in rasterlist:
        if not Quiet: print "{Apply_Linear_Correction} Correcting " + raster
        image,metadata = Raster_to_Numpy(raster,"float32")
        new_NoData = floor
        
        output = image * factor + offset
        low_value_indices = output < new_NoData
        output[low_value_indices] = new_NoData
        
        if save:
            outname = Create_Outname(outdir,raster,suffix)
            Numpy_to_Raster(output, metadata, outname, new_NoData ,"float32")
            
    if not Quiet: print "{Apply_Linear_Correction} Finished! \n "      
    return(image,metadata)

#=========================================================================================
def Temporal_Data_Fill(filelist,Quiet=False):

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
    print 'if you need it ASAP, contact the geoinformatics YPs!'
    
    return

#=========================================================================================
def Find_Overlap(file_A, NoData_A, file_B, NoData_B, outpath, Quiet=False):

    """
     Finds overlaping area between two raster images.
     
     this function examines two images and outputs a raster identifying pixels where both
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
    if not IsRaster(file_A) or not IsRaster(file_B):
        print '{Find_Overlap} both inputs must be rasters!'

    # spatially match the rasters
    print '{Find_Overlap} preparing input rasters!'
    Clip_and_Snap_Raster(file_A,file_B,file_B,False,NoData_B)
    
    # load the rasters as numpy arays.
    a,metaA = Raster_to_Numpy(file_A)
    b,metaB = Raster_to_Numpy(file_B)

    Workmatrix = numpy.zeros((metaA.Ysize,metaA.Xsize))
    Workmatrix = Workmatrix.astype('uint8')

    a[(a >= NoData_A*0.99999) & (a <= NoData_A*1.00001)] = int(1)
    b[(b >= NoData_B*0.99999) & (b <= NoData_B*1.00001)] = int(1)

    print '{Find_Overlap} Finding overlaping pixels!'
    Workmatrix = a + b
    Workmatrix[Workmatrix <2] = int(0)
    Workmatrix[Workmatrix >2] = int(2)
                
    print '{Find_Overlap} Saving overlap file!'          
    Numpy_to_Raster(Workmatrix, metaA, outpath,'0','uint8',False)
    Set_Null_Values(outpath,0,False)
    arcpy.RasterToPolygon_conversion(outpath, outpath[:-4]+'.shp', 'NO_SIMPLIFY')
    
    return metaA, metaB

#=========================================================================================
def Spatially_Match_Rasters(snap_raster,rasterlist,outdir,numtype=False,NoData_Value=False,
                            resamp_type=False,Quiet=False):

    """
    Prepares input rasters for further numerical processing
    
     This function simply ensures all rasters in "rasterlist" are identically projected
     and have the same cell size, then calls the Clip_and_Snap_Rasters function to ensure
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
    
    rasterlist = Enforce_Rasterlist(rasterlist)
    Exists(snap_raster)
    usetemp=False

    # set the snap raster environment in arcmap.
    arcpy.env.snapRaster=snap_raster

    print '{Spatially_Match_Rasters} Loading snap raster: ',snap_raster
    _,snap_meta = Raster_to_Numpy(snap_raster)
    print '{Spatially_Match_Rasters} Bounds of rectangle to define boundaries: [',snap_meta.rectangle,']'

    # for every raster in the raster list, snap rasters and clip.
    for rastname in rasterlist:
        
        _,meta = Raster_to_Numpy(rastname)
        head,tail=os.path.split(rastname)
        tempname=os.path.join(tempdir,tail)

        if snap_meta.projection.projectionName != meta.projection.projectionName:
            print '{Spatially_Match_Rasters} The files are not the same projection!'
            Project_Files(rastname,snap_raster,tempname,resamp_type,snap_raster)
            usetemp=True

        if round(float(snap_meta.cellHeight)/float(meta.cellHeight),5)!=1 and \
        round(float(snap_meta.cellWidth)/float(meta.cellWidth),5)!=1:

            if resamp_type:
                arcpy.Resample_management(rastname,tempname,snap_raster, resamp_type)
                usetemp=True
                
            print '{Spatially_Match_Rasters} The files are not the same resolution!'
            print '{Spatially_Match_Rasters} Resample the images manually or input a value for "resampe_type"!'

        # define an output name and run the Clip_ans_Snap_Raster function on formatted tifs.
        head,tail=os.path.split(rastname)
        outname=os.path.join(outdir,tail[:-4]+'_matched.tif')

        # if a temporary file was created in previous steps, use that one for clip and snap               
        if usetemp:   
            Clip_and_Snap_Raster(snap_raster,tempname,outname,numtype,NoData_Value,False)
        else:
            Clip_and_Snap_Raster(snap_raster,rastname,outname,numtype,NoData_Value,False)  
        print '{Spatially_Match_Rasters} Finished matching raster!'

    shutil.rmtree(tempdir)
    return

#=========================================================================================
def Clip_and_Snap_Raster(snap_raster, rastname, outname, numtype = False , NoData_Value = False):

    """
    Ensures perfect coincidence between a snap_raster and any input rasters
    
     This script is primarily intended for calling by the "Spatially_Match_Rasters" function
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
       snap_meta       metadata of the snap_raster file as output by Raster_to_Numpy
       meta            metadata of the rastername file as output by Raster_to_Numpy

     
    """

    # grab metadata for rastname
    _,snap_meta = Raster_to_Numpy(snap_raster)
    _,meta      = Raster_to_Numpy(rastname)

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
    print '{Clip_and_Snap_Raster} Clipping '+rastname
    tempout=os.path.join(tempdir,tail)
    try:    arcpy.Clip_management(rastname,snap_meta.rectangle, tempout,"#","#","NONE","MAINTAIN_EXTENT")
    except: arcpy.Clip_management(rastname,snap_meta.rectangle, tempout,"#","#","NONE")
    
    # load the newly cliped raster, find the offsets
    raster,meta = Raster_to_Numpy(tempout)
    xoffset = int(round((meta.Xmin - snap_meta.Xmin)/meta.cellWidth,0))
    yoffset = int(round((meta.Ymin - snap_meta.Ymin)/meta.cellHeight,0))

    # first iteration of clip with snap_raster environment sometimes has rounding issues
    # run clip a second time if raster does not fully lie within the extents of the bounding box
    if meta.Xsize > snap_meta.Xsize or meta.Ysize > snap_meta.Ysize:
        arcpy.Clip_management(tempout,snap_meta.rectangle, tempout[:-4] + '2.tif',"#","#","NONE")

        # reload and recalculate offsets
        raster,meta = Raster_to_Numpy(tempout[:-4] + '2.tif')
        xoffset = int(round((meta.Xmin - snap_meta.Xmin)/meta.cellWidth,0))
        yoffset = int(round((meta.Ymin - snap_meta.Ymin)/meta.cellHeight,0))

    # plop the snaped raster into the new output raster, alter the metadata, and save it
    meta.Xmin = snap_meta.Xmin
    meta.Ymin = snap_meta.Ymin
    Yrange= range(yoffset,(yoffset + meta.Ysize))
    Xrange= range(xoffset,(xoffset + meta.Xsize))

    # create empty matrix of NoData_Values to store output
    print('{Clip_and_Snap_Raster} Saving formated file' + rastname)
    newraster=numpy.zeros((snap_meta.Ysize,snap_meta.Xsize))+float(meta.NoData_Value)
    newraster[(snap_meta.Ysize - meta.Ysize - yoffset):(snap_meta.Ysize - yoffset),
              xoffset:(xoffset + meta.Xsize)] = raster[:,:]
    Numpy_to_Raster(newraster,meta,outname,NoData_Value,numtype,False)

    # clean up
    shutil.rmtree(tempdir)
    return snap_meta,meta

#=========================================================================================
def Clip_Rasters_to_Shape(rasterlist, shapefile, outdir = False):

    """
     Simple batch clipping script to clip rasters to shapefiles. 

     Inputs:
       rasterlist      single file, list of files, or directory for which to clip rasters
       shapefile       shapefile to which rasters will be clipped
       outdir          desired output directory. If no output directory is specified, the
                       new files will simply have '_c' added as a suffix. 

     
    """

    rasterlist=Enforce_Rasterlist(rasterlist)

    # ensure output directory exists
    if outdir and not os.path.exists(outdir):
        os.makedirs(outdir)

    for raster in rasterlist:

        # create output filename with "c" suffix
        outname = Create_Outname(outdir,raster,'c')
        
        # perform double clip , first using clip_management (preserves no data values)
        # then using arcpy.sa module which can actually do clipping geometry unlike the management tool.
        arcpy.Clip_management(raster,"#",outname,shapefile,"ClippingGeometry")
        out = sa.ExtractByMask(outname,shapefile)
        out.save(outname)
        print("{Clip_Rasters_to_Shape} Clipped and saved: " + outname)

    print("{Clip_Rasters_to_Shape} Clipping complete! \n")
    
    return

#=========================================================================================
def Raster_to_Numpy(Raster, num_type=False):

    """
    Wrapper for arcpy.RasterToNumpyArray with better metadata handling
    
     This is just a wraper for the RasterToNumPyArray function within arcpy, but it also
     extracts out all the spatial referencing information that will probably be needed
     to save the raster after desired manipulations have been performed.
     also see Numpy_to_Raster function in this module.

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
       call this function with  " rast,Metadata = Raster_to_Numpy(Raster) "
       perform numpy manipulations as you please
       then save the array with " Numpy_to_Raster(rast,Metadata,output)   "
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
    if IsRaster(Raster):

        numpy_rast  = arcpy.RasterToNumPyArray(Raster)
        Metadata    = metadata(numpy_rast)
        
        if num_type:
            numpy_rast = numpy_rast.astype(num_type)
            
    else:  
        print("{Raster_to_Numpy} Raster '{0}'does not exist".format(Raster))
    
    
    
    return numpy_rast, Metadata

#=========================================================================================
def Numpy_to_Raster(numpy_rast, Metadata, outpath, NoData_Value = False, num_type = False):

    """
    Wrapper for arcpy.NumPyArrayToRaster function with better metadata handling
    
     this is just a wraper for the NumPyArrayToRaster function within arcpy. It is used in
     conjunction with Raster_to_Numpy to streamline reading image files in and out of numpy
     arrays. It also ensures that all spatial referencing and projection info is preserved
     between input and outputs of numpy manipulations.

     inputs:
       numpy_rast          the numpy array version of the input raster
       Metadata            The variable exactly as output from "Raster_to_Numpy"
       outpath             output filepath of the individual raster
       NoData_Value        the no data value of the output raster
       num_type            must be a string equal to any of the types listed at the following
                           address [http://docs.scipy.org/doc/numpy/user/basics.types.html]
                           for example: 'uint8' or 'int32' or 'float32'

     Usage example:
       call Raster_to_Numpy with  " rast,Metadata = Raster_to_Numpy(Raster) "
       perform numpy manipulations as you please
       then save the array with " Numpy_to_Raster(rast,Metadata,output)   "

     
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
    
    print("{Numpy_to_Raster} Saved output file as {0}".format(outpath))

    return

#=========================================================================================
def Many_Raster_Stats(rasterlist, low_thresh, high_thresh, outdir, NoData_Value, saves = ['AVG','NUM','STD']):

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

#=========================================================================================
def Rolling_Raster_Stats(centers, windows, window_width, low_thresh, high_thresh, outdir,
                    NoData_Value, chunks=False, start_chunk=False, saves = ['AVG','NUM','STD']):

    """
    Takes rolling statistics on time series raster data.

     Similar to "Many_Raster_Stats" but with optimization for statistics across many
     partially overlapping datasets and the ability to handle extremely large datasets.

     this function was built specifically for the Langley Northwest Agriculture team in
     Fall of 2014. It was designed to perform statistics on many raster blocks as output from
     the 'Rolling_Window' function, therefore its inputs include centers, windows, and window width.

     the function was used to take moving averages of MODIS land surface temperature data
     where efficiency could be gained by keeping data loaded for one window in memory for
     the next window, since 80% or more of each window overlaps with the previous one. This
     very significantly reduced processing time, but required chunking data to avoid hitting
     pythons 2GB memory limit (32 bit version).

     Inputs:
       centers         Array of filenames representing the center of each list in "windows".
       windows         2d array of filenames. window groupings as output from "Rolling_Window".
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

     , Lauren Makely
    """

    saves=core.Enforce_List(saves)
    
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
    temp,meta=Raster_to_Numpy(windows[0][0])
    xs,ys=temp.shape
    zs=len(windows[0])
    xyzs=xs*ys*zs

    # automatically determine number of chunks to use by limiting the size of
    # any given data brick to 3 million values
    if not chunks: chunks=xyzs/3000000+1

    # find the dimensions of the chunks for subprocessing of the data
    # data is split into chunks to avoid hitting the python 2gb memory limit.
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
                        tempmatrix,x,y,w,h,spat_ref = Raster_to_Numpy(Raster)
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
                    Raster_to_Numpy(average,x,y,w,h,spat_ref,chunk_average_name)
                    chunk_average_list.append(chunk_average_name)
                    
                if 'NUM' in saves:
                    Raster_to_Numpy(count,x,y,w,h,spat_ref,chunk_average_name)
                    chunk_count_list.append(chunk_count_name)
                    
                if 'STD' in saves:
                    Raster_to_Numpy(Std,x,y,w,h,spat_ref,chunk_average_name)
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

                temp,x,y,w,h,spat_ref = Raster_to_Numpy(Avg_chunk)
                out_Avg[:,ychunk]=temp[:,range(len(ychunk))]
                
            Numpy_to_Raster(out_Avg,x,y,w,h,spat_ref,average_name)
            
        if 'NUM' in saves:
            for chunkID,ychunk in enumerate(ychunks):
                Num_chunk= os.path.join(tempdir,'.'.join(tail.split('.')[:-1])+
                    '_W'+str(window_width).zfill(2)+'_C'+info.year+info.j_day+'_Num_Chnk'+str(chunkID)+'.tif')      

                temp,x,y,w,h,spat_ref = Raster_to_Numpy(Num_chunk)
                out_Num[:,ychunk]=temp[:,range(len(ychunk))]
            
            Numpy_to_Raster(out_Num,x,y,w,h,spat_ref,count_name)
            
        if 'STD' in saves:
            for chunkID,ychunk in enumerate(ychunks):
                Std_chunk= os.path.join(tempdir,'.'.join(tail.split('.')[:-1])+
                    '_W'+str(window_width).zfill(2)+'_C'+info.year+info.j_day+'_Std_Chnk'+str(chunkID)+'.tif')       
                
                temp,x,y,w,h,spat_ref = Raster_to_Numpy(Std_chunk)
                out_Std[:,ychunk]=temp[:,range(len(ychunk))]

            Numpy_to_Raster(out_Std,x,y,w,h,spat_ref,std_name)
            
    print '{Rolling_Raster_Stats} Finished with all processing!'
    
    return

#=========================================================================================
def Calc_Degree_Days(T_base, Max, Min, NoData_Value,
                             outpath=False, roof=False, floor=False, Quiet=False):

    """
    Inputs rasters for maximum and minimum temperatures, calculates Growing Degree Days
    
     this function is built to perform the common degree day calculation on either a pair
     of raster filepaths, a pair of numpy arrays, or a pair of lists. It requires, at minimum
     A maximum temperature value, a minimum temperature value, and a base temperature.
     This equation could also be used to calculate Chill hours or anything similar. 

     The equation is as follows:
                                   [(Max+Min)/2 + T_base]

     where values in Max which are greater than roof are set equal to roof
     where values in Min which are lesser than floor are set equal to floor
     consult [https://en.wikipedia.org/wiki/Growing_degree-day] for more information.

     Inputs:
       T_base          base temperature to ADD, be mindful of sign convention.
       Max             filepath, numpy array, or list of maximum temperatures
       Min             filepath, numpy array, or list of minimum temperatures
       NoData_Value    values to ignore (must be int or float)
       outpath         filepath to which output should be saved. Only works if Max and Min inputs
                       are raster filepaths with spatial referencing.
       roof            roof value above which Max temps do not mater
       floor           floor value below which Min temps do not mater
       Quiet           Set True to supress output

     Outputs:
       degree_days     numpy array of output values. This same data is saved if outpath is
                       not left at its default value of False.

     , Lauren Makely
    """

    # format numerical inputs as floating point values
    T_base= float(T_base)
    if roof:  roof  = float(roof)
    if floor: floor = float(floor)

    # Determine the type of input and convert to useful format for calculation
    # acceptable input formats are filepaths to rasters, numpy arrays, or lists.
    if type(Max) is list and type(Min) is list:
        
        # if the first entry in a list is a string, asume it is a filename that has
        # been placed into a list.
        if type(Max[0]) is str and type(Min[0]) is str:
            Max=Max[0]
            Min=Min[0]

            # load in the min and max files.
            highs, meta = Raster_to_Numpy(Max)
            lows, meta  = Raster_to_Numpy(Min)

            if not Quiet: print '{Calc_Degree_Days} Found spatialy referenced image pair!'
        else:
            highs = numpy.array(Max)
            lows  = numpy.array(Min)
            
    # if they are already numpy arrays
    elif type(Max) is numpy.ndarray:
            highs=Max
            lows =Min
            
# Begin to perform the degree day calculations.....................

    # apply roof and floor corrections if they have been specified
    if roof:  highs[highs >= roof] = roof
    if floor: lows[lows <=floor] = floor

    # find the shapes of high and low arrays
    xsh,ysh=highs.shape
    xsl,ysl=lows.shape

    # only continue if min and max arrays have the same shape
    if xsh==xsl and ysh==ysl:
        
        # set empty degree day matrix
        degree_days=numpy.zeros((xsh,ysh))
        
        # peform the calculation
        for x in range(xsh):
            for y in range(ysh):
                if round(highs[x,y]/NoData_Value,10) !=1 and round(lows[x,y]/NoData_Value,10) != 1:
                    degree_days[x,y]=((highs[x,y] + lows[x,y])/2) + T_base
                else:
                    degree_days[x,y]=NoData_Value
                
    # print error if the arrays are not the same size
    else:
        print '{Calc_Degree_Days} Images are not the same size!, Check inputs!'
        return(False)

    # if an output path was specified, save it with the spatial referencing information.
    if outpath and type(Max) is str and type(Min) is str:
        Numpy_to_Raster(degree_days, meta, outpath)
        print '{Calc_Degree_Days} Output saved at : ' + outpath
        
    return(degree_days)

#=========================================================================================
def Accum_Degree_Days(rasterlist, critical_values = False, outdir = False):

    """
    Accumulates degree days in a time series rasterlist
    
     This function is the logical successor to Calc_Degree_Days. Input a list of rasters
     containing daily data to be accumulated. Output raster for a given day will be the sum
     total of the input raster for that day and all preceding days. The last output raster in
     a years worth of data (image 356) would be the sum of all 365 images. The 25th output
     raster would be a sum of the first 25 days.
     Critical value rasters will also be created. Usefull for example: we wish to know on what day
     of our 365 day sequence every pixel hits a value of 100. Input 100 as a critical value
     and that output raster will be generated. 

     Inputs:
       rasterlist          list of files, or directory containing rasters to accumulate
       critical_values     Values at which the user wishes to know WHEN the total accumulation
                           value reaches this point. For every critical value, an output
                           raster will be created. This raster contains integer values denoting
                           the index number of the file at which the value was reached.
                           This input must be a list of ints or floats, not strings.
       outdir              Desired output directory for all output files.

     Warnings:
       Do not input "0" as a critical value. if you wish to know when something becomes positive
       please use a small floating point value such as "0.001"

     Authors: Fall2014: Lauren Makely, Jeffry Ely
    """

    rasterlist = Enforce_Rasterlist(rasterlist)
    if critical_values:
        critical_values = Enforce_List(critical_values)
    if outdir and not os.path.exists(outdir):
        os.makedirs(outdir)

    for i,raster in enumerate(rasterlist):

        image,meta = Raster_to_Numpy(raster,"float32")
        print "{Accum_Degree_Days} Loaded " + raster
        xs,ys = image.shape

        if i==0:
            Sum = numpy.zeros((xs,ys))
            Crit= numpy.zeros((len(critical_values),xs,ys))
        
        if image.shape == Sum.shape:

            # only bother to proceed if at least one pixel is positive
            if numpy.max(image) >= 0:
                for x in range(xs):
                    for y in range(ys):

                        if image[x,y] >= 0:
                            Sum[x,y] = Sum[x,y]+image[x,y]

                        if critical_values:    
                            for z,critical_value in enumerate(critical_values):
                                if Sum[x,y] >= critical_value and Crit[z,x,y]==0:
                                    Crit[z,x,y] = i
        else:
            print "{Accum_Degree_Days} Encountered an image of incorrect size! Skipping it!"

        Sum = Sum.astype('float32')
        outname = Create_Outname(outdir, raster, "Accum")
        Numpy_to_Raster(Sum, meta, outname)

        # collect garbage
        del image
        gc.collect()

    # output critical accumulation rasters.
    Crit = Crit.astype('int16')
    crit_meta = meta
    crit_meta.NoData_Value = 0
    head , tail = os.path.split(outname)        # place these in the last raster output location
    for z,critical_value in enumerate(critical_values): 
        outname = os.path.join(head,"Crit_Accum_Index_Val-{0}.tif".format(str(critical_value)))
        print "Saving :",outname
        Numpy_to_Raster(Crit[z,:,:], crit_meta, outname)

    del Crit                       
    return

#=========================================================================================
def Resample_Filelist(rasterlist,reference_cellsize,resamp_type,outdir=False,Quiet=False):

    """
     Simple a batch processor for resampling with arcmap

     Inputs:
       rasterlist          list of rasters to resample
       reference_cellsize  Either a cell size writen as "10 10" for example or a reference
                           raster file to match cell sizes with. 
       resamp_type         The resampling type to use if images are not identical cell sizes.
                               "NEAREST","BILINEAR","CUBIC","MAJORITY" are the options.
       outdir              output directory to save files. if left "False" output files will
                           be saved in same folder as the input file.

     
    """

    # sanitize inputs and create directories
    reference_cellsize=str(reference_cellsize)
    rasterlist=Enforce_Rasterlist(rasterlist)
    if outdir and not os.path.isdir(outdir):
        os.makedirs(outdir)
        
    # resample the files.
    for filename in rasterlist:

        # create output filename
        outname = Create_Outname(outdir,filename,'rs')
        
        #arcpy.Resample_management(filename,,reference_cellsize, resamp_type)
    
    return

#=========================================================================================
def Project_Filelist(filelist, reference_file, outdir=False, resampling_type=False,
                      cell_size=False, Quiet=False):

    """
    Wrapper for multiple arcpy projecting functions. Projects to reference file
    
     Inputs a filelist and a reference file, then projects all rasters or feature classes
     in the filelist to match the projection of the reference file. Writes new files with a
     "_p" appended to the end of the input filenames.

     Inputs:
       filelist            list of files to be projected
       outdir              optional desired output directory. If none is specified, output files
                           will be named with '_p' as a suffix.
       reference_file      Either a file with the desired projection, or a .prj file.
       resampling type     exactly as the input for arcmaps project_Raster_management function
       cell_size           exactly as the input for arcmaps project_Raster_management function

     Output:
       Spatial reference   spatial referencing information for further checking.

     
    """

    # sanitize inputs 
    Exists(reference_file)
    rasterlist  = Enforce_Rasterlist(filelist)
    featurelist = Enforce_Featurelist(filelist)
    cleanlist = rasterlist + featurelist

    # ensure output directory exists
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        
    # grab data about the spatial reference of the reference file. (prj or otherwise)
    if reference_file[-3:]=='prj':
        Spatial_Reference=arcpy.SpatialReference(Spatial_Reference)
    else:
        Spatial_Reference=arcpy.Describe(reference_file).spatialReference
        
    # determine wether coordinate system is projected or geographic and print info
    if Spatial_Reference.type=='Projected':
        if not Quiet:
            print('{Project_Filelist} Found ['+ Spatial_Reference.PCSName +
                    '] Projected coordinate system')
    else:
        if not Quiet:
            print('{Project_Filelist} Found ['+ Spatial_Reference.GCSName +
                    '] Geographic coordinate system')

    for filename in cleanlist:
        
        # create the output filename
        outname = Create_Outname(outdir,filename,'p')

        # Perform the projection!...................................................
        # use ProjectRaster_management for rast files
        if IsRaster(filename):
            if resampling_type:
                arcpy.ProjectRaster_management(filename,outname,Spatial_Reference,
                            resampling_type)
            else:
                arcpy.ProjectRaster_management(filename,outname,Spatial_Reference)
                
        # otherwise, use Project_management for featureclasses and featurelayers
        else:
            arcpy.Project_management(filename,outname,Spatial_Reference)

        # print a status update    
        if not Quiet: print '{Project_Filelist} Wrote projected file to ' + outname

    if not Quiet: print '{Project_Filelist} Finished! \n '
    return(Spatial_Reference)

#=========================================================================================
def Rolling_Window(filelist, window_size, start_jday, end_jday,
                                           start_year=False, end_year=False, Quiet=False):

    """
    Creates a list of windows each containing a list of files grouped by central date
    
     this function calls the 'Files_in_Window' function for a whole range of dates to produce
     rolling windows. Use this if you intend to iterate through many files for rolling
     statistics
     
     Inputs:
       filelist        the list of files to include in the rolling window. This could be
                       easily created with the List_Files function.
       window_size     width of the window in days. used to group files
       start_jday      julian day on which to start the window centers
       end_jday        julian day on which to end the window centers
       start_year      year on which to start the window centers. If you wish to bin all days
                       at a given point in the year together for long term averages, leave
                       year inputs blank or set to 'False'. This will then consider all
                       julian days within the window for all years in 'filelist'
       end_year        year on which to end the window centers. If you wish to bin all days
                       at a given point in the year together for long term averages, leave
                       year inputs blank or set to 'False'. This will then consider all
                       julian days within the window for all years in 'filelist'

     Outputs:
       window_centers  list of window center names
       window_matrix   list of all files in grouping around each window center

     
    """
    
    # set intial conditions for while loop
    index=0
    current_jday=start_jday
    current_year=start_year
    window_matrix=[]
    window_centers=[]

    filelist=Enforce_Filelist(filelist)

    # if a start year and end year exist (not False)
    if start_year and end_year:

        # loop for as long as the current year and day do not exceed the ending year and day
        while current_jday <= end_jday and current_year <=end_year:
            center,window= Files_in_Window(filelist,window_size,current_jday,current_year,Quiet)
            window_matrix.append(window)
            window_centers.append(center)

            # if the current day counter has reached the end of the year, reset the day
            # and advance the year count forward
            if current_jday==365 and not current_year%4==0:
                current_jday=1
                current_year=current_year + 1
            elif current_jday==366 and current_year%4==0:
                current_jday==1
                current_year=current_year + 1
            else:
                current_jday=current_jday + 1
                index=index+1
                
    # if years are set to False, process based soley on julian days.
    else:
        
        # loop for as long as the current day does not exceed the ending day
        while current_jday <= end_jday:
            center,window= Files_in_Window(filelist,window_size,current_jday,False,Quiet)
            window_matrix.append(window)
            window_centers.append(center)
            
            # if the user has chosen to ignore years, the code must stop at day 366.
            if current_jday==366:
                return window_centers,window_matrix
            else:
                current_jday=current_jday + 1
            index=index+1

    if not Quiet: print '{Rolling_Window} Finished!'
        

    return window_centers,window_matrix

#=========================================================================================
def Files_in_Window(filelist, window_size, jday, year=False, Quiet=False):

    """
    Uses grab_data_info to bin raster data by date
    
     this function returns a list of files within the window designation.
     This is useful for feeding into functions that create weekly/monthly/annual statistics
     from daily data. Use the Rolling_Window function (which calls this one) if you intend
     to iterate through many files for rolling statistics.

     This function only works for files whos naming conventions are supported by the
     'Grab_Data_Info' function, and relies upon the attributes stored in info.year and
     info.j_day
     
     Inputs:
       filelist        the list of files to include in the window. This could be easily
                       created with the List_Files function.
       window_size     width of the window in days. used to group files
       jday            the julian day at which to center the window
       year            the year on which to center the window. If you wish to bin all days
                       at a given point in the year together for long term averages, leave
                       year input blank or set to 'False'. This will then consider all
                       julian days within the window for all years in 'filelist'

     Outputs:
       center          A file representing the center of the window, useful in naming.
       in_window       outputs only the files within the specified window.

     
    """
    
    # initialize empty lists for tracking
    in_window=[]
    yearlist=[]
    jdaylist=[]
    center_file=False

    # sanitize inputs
    jday=int(jday)
    window_size=int(window_size)
    filelist=Enforce_Filelist(filelist)
    
    # define list of acceptable values
    
    # if the window is an even number, it has to be centered on the half day
    # if the window is an odd number, it can be centered exactly on the day
    if window_size%2==0:
        window=range(-(window_size/2)+1,(window_size/2)+1)                   
    else:
        window=range(-((window_size-1)/2),((window_size-1)/2)+1)

    # generate concurent lists of acceptable parameters
    for day in window:
        if year:
            date= datetime.datetime(year,1,1) + datetime.timedelta(day+jday-1)
            yearlist.append(str(date.year))
        else:
            date= datetime.datetime(2010,1,1) + datetime.timedelta(day+jday-1)
        jdaylist.append(str(date.strftime('%j')))

    # if window is not year specific, make sure we include 366 when appropriate
    if not year and '365' in jdaylist and '001' in jdaylist:
        jdaylist.append('366')

    # gather statistics on the filelist.
    for item in filelist:
        info=Grab_Data_Info(item,False,True)

        if year:
            # checks to see if both day and year are on the respective lists
            if info.j_day in jdaylist and info.year in yearlist:

                # further verifies that they are for concurent list entries (not mismatched)
                if yearlist[jdaylist.index(info.j_day)]==info.year:
                    in_window.append(item)
                    
                    # if this files info indicates it is on the center julian day, save this info
                    if info.j_day==str(jday).zfill(3):
                        center_file=item
        else:
            # checks to make sure day only is within the window, without considering year
            if info.j_day in jdaylist:
                in_window.append(item)

                # if this files info indicates it is on the center julian day, save this info
                if info.j_day==str(jday).zfill(3):
                    center_file=item
                
    if not Quiet:
        if year:
            print('{Files_in_Window} Found ' + str(len(in_window)) + ' files in ['+ str(window_size) + 
                  ']day window: '+ str(jday) +'-'+ str(year))
        else:
            print('{Files_in_Window} Found ' + str(len(in_window)) + ' files in ['+ str(window_size) + 
                  ']day window: '+ str(jday))
 
    return center_file,in_window

#=========================================================================================
def List_Files(recursive, Dir, Contains=False, DoesNotContain=False, Quiet=False):

    """
    Simple file listing function with more versatility than python builtins or arcpy.List
    
     This function sifts through a directory and returns a list of filepaths for all files
     meeting the input criteria. Useful for discriminatory iteration or recursive searches.
     Could be used to find all tiles with a given datestring such as 'MOD11A1.A2012', or
     perhaps all Band 4 tiles from a directory containing landsat 8 data.

     Inputs:
           recursive       'True' if search should search subfolders within the directory
                           'False'if search should ignore files in subfolders.
           Dir             The directory in which to search for files meeting the criteria
           Contains        search criteria to limit returned file list. File names must
                           contain parameters listed here. If no criteria exists use 'False'
           DoesNotContain  search criteria to limit returned file list. File names must not
                           contain parameters listed here. If no criteria exists use 'False'
           Quiet           Set Quiet to 'True' if you don't want anything printed to screen.
                           Defaults to 'False' if left blank.
     Outputs:
           filelist        An array of full filepaths meeting the criteria.

     Example Usage:
           import ND
           filelist=ND.List_Files(True,r'E:\Landsat7','B1',['gz','xml','ovr'])

           The above statement will find all the Band 1 tifs in a landsat data directory
           without including the associated metadata and uncompressed gz files.
           "filelist" variable will contain full filepaths to all files found.

     
    """
    
    # import modules and set up empty lists
    filelist=[]
    templist=[]

    # ensure input directory actually exists
    if not Exists(Dir): return(False)

    # Ensure single strings are in list format for the loops below
    if Contains: Contains = Enforce_List(Contains)
    if DoesNotContain:
        DoesNotContain = Enforce_List(DoesNotContain)
        DoesNotContain.append('sr.lock')    # make sure lock files don't get counted
    else:
        DoesNotContain=['sr.lock']          # make sure lock files don't get counted
    
    # use os.walk commands to search through whole directory if recursive
    if recursive:
        for root,dirs,files in os.walk(Dir):
            for basename in files:
                filename = os.path.join(root,basename)
                
                # if both conditions exist, add items which meet Contains criteria
                if Contains and DoesNotContain:
                    for i in Contains:
                        if i in basename:
                            templist.append(filename)
                    # if the entire array of 'Contains' terms were found, add to list
                    if len(templist)==len(Contains):
                        filelist.append(filename)
                    templist=[]
                    # remove items which do not meet the DoesNotcontain criteria
                    for j in DoesNotContain:
                        if j in basename:
                            try: filelist.remove(filename)
                            except: pass
                                    
                # If both conditions do not exist (one is false)                        
                else:
                    # determine if a file is good. if it is, add it to the list.
                    if Contains:
                        for i in Contains:
                            if i in basename:
                                templist.append(filename)
                        # if the entire array of 'Contains' terms were found, add to list
                        if len(templist)==len(Contains):
                            filelist.append(filename)
                        templist=[]

                    # add all files to the list, then remove the bad ones.        
                    elif DoesNotContain:
                        filelist.append(filename)
                        for j in DoesNotContain:
                            if j in basename:
                                try: filelist.remove(filename)
                                except: pass
                    else:
                        filelist.append(filename)
                                        
                # if neither condition exists
                    if not Contains and not DoesNotContain:
                        filelist.append(filename)

    # use a simple listdir if recursive is False
    else:
        # list only files in current directory, not subdir and check criteria
        try:
            for basename in os.listdir(Dir):
                filename = os.path.join(Dir,basename)
                if os.path.isfile(filename):
                    if Contains:
                        for i in Contains:
                            if i in basename:
                                templist.append(filename)
                            
                        # if the entire array of 'Contains' terms were found, add to list
                        if len(templist)==len(Contains):
                            filelist.append(filename)
                        templist=[]
                    else:
                        filelist.append(filename)
        
                # Remove any files from the filelist that fail DoesNotContain criteria
                if DoesNotContain:
                    for j in DoesNotContain:
                        if j in basename:
                            try: filelist.remove(filename)
                            except: pass            
        except: pass
        
    # Print a quick status summary before finishing up if Quiet is False
    if not Quiet:
        print '{List_Files} Files found which meet all input criteria: ' + str(len(filelist))
        print '{List_Files} finished! \n'
    
    return(filelist)

#=========================================================================================
def Set_Null_Values(filelist, NoData_Value, Quiet=False):

    """
    Simple batch NoData setting function. Makes raster data more arcmap viewing friendly
    
     Function inputs a list of raster (usually tifs) files and sets no data values. This
     function does not actually change the raster values in any way, and simply defines which
     numerical values to be considered NoData in metadata.

     inputs:
       filelist        list of files for which to set NoData values. easily created with
                       "List_Files" function
       NoData_Value    Value to declare as NoData (usually 0 or -9999)
       Quiet           Set Quiet to 'True' if you don't want anything printed to screen.
                       Defaults to 'False' if left blank.

     , Lauren Makely
    """

    filelist = Enforce_Rasterlist(filelist)

    # iterate through each file in the filelist and set nodata values
    for filename in filelist:

        arcpy.SetRasterProperties_management(filename,data_type="#",statistics="#",
                    stats_file="#",nodata="1 "+str(NoData_Value))
        if not Quiet:
            print '{Set_Null_Values} Set NoData values in ' + filename
               
    if not Quiet:print '{Set_Null_Values} Finished! \n'            
    return

#=========================================================================================
def Set_Range_to_Null(filelist,above,below,NoData_Value,Quiet=False):

    """
    Changes values within a certain range to NoData
    
     similar to Set_Null_Values, but can take an entire range of values to set to NoData.
     useful in filtering obviously erroneous high or low values from a raster dataset.

     inputs:
       filelist    list of files for which to set NoData values. easily created with
                       "List_Files" function
       above       will set all values above this, but below "below" to NoData
                       set to 'False' if now upper bound exists
       below       will set all values below this, but above "above" to NoData
                       set to 'False' if no lower bound exists
       Quiet       Set Quiet to 'True' if you don't want anything printed to screen.
                       Defaults to 'False' if left blank.

     , Lauren Makely
    """

    # sanitize filelist input
    filelist=Enforce_Rasterlist(filelist)

    # iterate through each file in the filelist and set nodata values
    for filename in filelist:
        #load raster as numpy array and save spatial referencing.
        raster, meta=Raster_to_Numpy(filename)

        if above and below:
            raster[raster <= below and raster >= above] = NoData_Value
        elif above:
            raster[raster >= above] = NoData_Value
        elif below:
            raster[raster <= below] = NoData_Value
            
        Numpy_to_Raster(raster, meta, filename)
        arcpy.SetRasterProperties_management(filename,data_type="#",statistics="#",
                    stats_file="#",nodata="1 "+str(NoData_Value))
        
        if not Quiet:
            print '{Set_Range_to_Null} Set NoData values in ' + filename

    if not Quiet:print '{Set_Range_to_Null} Finished!'            
    return

#=========================================================================================
def Remove_Empty_Folders(path):

    """Removes empty folders, used for cleaning up temporary workspace."""

    import os

    # only continue if the path exists
    if os.path.isdir(path):

        # list files in directory
        files = os.listdir(path)
        
        # if zero files exist inside it, delete it.
        if len(files)==0:
            os.rmdir(path)
            return(True)
        
    return(False)

#=========================================================================================
def Rename(filename,replacethis,withthis,Quiet=False):

    """
    Simply renames files

     Inputs:
       filename        input file to rename    
       replacethis     String to be replaced. such as " " (a space) 
       withthis        What to replace the string with. such as "_" (an underscore)
       Quiet           Set Quiet to 'True' if you don't want anything printed to screen.
                       Defaults to 'False' if left blank.

     Outputs:
           newfilename     returns the new name of the renamed file.

     
     """

    import os
    
    if replacethis in filename:

        # make sure the filename exists
        Exists(filename)

        # define a new filename
        newfilename=filename.replace(replacethis,withthis)

        # rename the file
        os.rename(filename,newfilename)

        # tell the user about it.
        if not Quiet: print '{Rename} Renamed',filename,'to',newfilename
        
        return newfilename
    else:
        return filename

#=========================================================================================
def Enforce_List(item):

    """
    Ensures input item is list format. 

     many functions within this module allow the user
     to input either a single input or list of inputs in string format. This function makes
     sure single inputs in string format are handled like single entry lists for iterative
     purposes. It also will output an error if it is given a boolean value to signal that
     an input somewhere else is incorrect.

     
     """

    if not isinstance(item,list) and item:
        return([item])
    
    elif isinstance(item,bool):
        print '{Enforce_List} Cannot enforce a bool to be list! at least one list type input is invalid!'
        return(False)
    else:
        return(item)
    
#=========================================================================================
def Enforce_Filelist(filelist):

    """
    Sanitizes file list inputs

    This function checks that the input is a list of files and not a directory. If the input
     is a directory, then it returns a list of ALL files in the directory. This is to allow
     all functions which input filelists to be more flexible by accepting directories instead.

     
    """
    
    if isinstance(filelist,str):
        if os.path.exists(filelist):
            new_filelist= List_Files(False,filelist,False,False,True)
            return(new_filelist)
        elif os.path.isfile(filelist):
            return([filelist])
    
    elif isinstance(filelist,bool):
        print 'Expected file list or directory but recieved boolean or None type input!'
        return(False)
    else:        return(filelist)
    
#=========================================================================================
def Enforce_Rasterlist(filelist):

    """
    Sanitizes raster list inputs

     This function works exactly like Enforce_Filelist, with the added feature of removing
     all filenames that are not of a raster type recognized by Arcmap.

     Input:    filelist        any list of files
     Output:   new_filelist    New list with all non-raster files in filelist removed.

     
    """

    # first place the input through the same requirements of any filelist
    filelist = Enforce_Filelist(filelist)
    new_filelist=[]

    for filename in filelist:
        if IsRaster(filename):
            new_filelist.append(filename)

    return(new_filelist)

#=========================================================================================
def Enforce_Featurelist(filelist):

    """
    Sanitizes feature list inputs

     This function works exactly like Enforce_Filelist, with the added feature of removing
     all filenames that are not of a feature class type recognized by arcmap.

     Input:    filelist        any list of files
     Output:   new_filelist    New list with all non-feature class files in filelist removed.

     Bugs:
       right now, all this does is check for a shape file extension. Sometimes shape files
       can be empty or otherwise contain no feature class data. This function does not check
       for this.

     
    """

    # first place the input through the same requirements of any filelist
    filelist=Enforce_Filelist(filelist)
    new_filelist=[]

    feat_types=['shp']

    for filename in filelist:
        ext=filename[-3:]

        if os.path.isfile(filename):
            for feat_type in feat_types:
                if ext == feat_type:
                    new_filelist.append(filename)

    return(new_filelist)

#=========================================================================================
def Grab_Data_Info(filepath,CustGroupings=False,Quiet=False):

    """
    Extracts in-filename metadata from common NASA data products

     This function simply extracts relevant sorting information from a MODIS or Landsat
     filepath of any type or product and returns object properties relevant to that data.
     it will be expanded to include additional data products in the future.

     Inputs:
           filepath        full or partial filepath to any modis product tile
           CustGroupings   User defined sorting by julian days of specified bin widths.
                           input of 5 for example will group January 1,2,3,4,5 in the first bin
                           and january 6,7,8,9,10 in the second bin, etc.
           Quiet           Set Quiet to 'True' if you don't want anything printed to screen.
                           Defaults to 'False' if left blank.
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
    path,name=os.path.split(filepath)
    
    # create an object class and the info object
    class Object(object):pass
    info = Object()

    # figure out what kind of data these files are. 
    data_type = Identify(name)

    # if data looks like MODIS data
    if data_type == 'MODIS':
        params=['product','year','j_day','tile','type','version','tag','suffix']
        n=name.split('.')
        end=n[4]
        string=[n[0],name[9:13],name[13:16],n[2],'MODIS',n[3],end[:13],end[13:]]
            
    # if data looks like Landsat data
    elif data_type =='Landsat':
        params=['sensor','satellite','WRSpath','WRSrow','year','j_day','groundstationID',
                'Version','band','type','suffix']
        n=name.split('.')[0]
        string=[n[1],n[2],n[3:6],n[6:9],n[9:13],n[13:16],n[16:19],
                n[19:21],n[23:].split('_')[0],'Landsat','_'.join(n[23:].split('_')[1:])]
            
    # if data looks like WELD CONUS data
    elif data_type == 'WELD_CONUS' or data_type == 'WELD_AK':
        params=['coverage','period','year','tile','start_day','end_day','type']
        n=name.split('.')
        string=[n[0],n[1],n[2],n[3],n[4][4:6],n[4][8:11],'WELD']
        # take everything after the first underscore as a suffix if one exists.
        if '_' in name:
            params.append('suffix')
            string.append('_'.join(name.split('_')[1:]))
            
    # if data looks like ASTER data
    elif data_type == 'ASTER':
        params=['product','N','W','type','period']
        n=name.split('_')
        string=[n[0],n[1][1:3],n[1][5:9],n[-1].split('.')[0],'none']
    
    # if data looks like TRMM data
    elif data_type == 'TRMM':
        print '{Grab_Data_Info} no support for TRMM data yet! you should add it!'
        return(False)

    # if data looks like AMSR_E data
    elif data_type == 'AMSR_E':
        print '{Grab_Data_Info} no support for AMSR_E data yet! you should add it!'
        return(False)

    # if data looks like AIRS data
    elif data_type == 'AIRS':
        print '{Grab_Data_Info} no support for AIRS data yet! you should add it!'
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
    # this attribute represent data that is produced from many dates, not just one.
    if not hasattr(info,'period'):
    # fill in date format values and custom grouping and season information based on julian day
    # many files are named according to julian day. we want the date info for these files
        try:
            tempinfo= datetime.datetime(int(info.year),1,1)+datetime.timedelta(int(int(info.j_day)-1))
            info.month  = tempinfo.strftime('%b')
            info.day    = tempinfo.day
        # some files are named according to date. we want the julian day info for these files
        except:
            fmt = '%Y.%m.%d'
            tempinfo= datetime.datetime.strptime('.'.join([info.year,info.month,info.day]),fmt)
            info.j_day = tempinfo.strftime('%j')

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
        CustGroupings=Enforce_List(CustGroupings)
        for grouping in CustGroupings:
            if type(grouping)==int:
                groupname='custom' + str(grouping)
                setattr(info,groupname,1+(int(info.j_day)-1)/(grouping))
            else:
                print('{Grab_Data_Info} invalid custom grouping entered!')
                print('{Grab_Data_Info} [CustGrouping] must be one or more integers in a list')

    # make sure the filepath input actually leads to a real file, then give user the info
    if Exists(filepath):
        if not Quiet:
            print '{Grab_Data_Info} '+ info.type + ' File ['+ name +'] has attributes '
            print vars(info)
        return(info)
    else: return(False)

#=========================================================================================
def Identify(name):

    """
    Compare filename against known NASA data file naming conventions to identify it

     Nested within the Grab_Data_Info function

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

    
    else:return(False)


#=========================================================================================
def Move_File(source,destination,Quiet=False):

    """Moves a file"""

    dest_path,name=os.path.split(destination)

    # create that directory if it doesnt already exist
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    try:     
        shutil.move(source,destination)
        if not Quiet:
            print '{Move_File} moved file : [' + source + ']'
    except:
        if not Quiet:
            print '{Move_File} Failed to move file : [' + source + ']'
        
    return(dest_path)

#=========================================================================================
def Exists(location):

    """Ensures inputlocation is either a file or a folder"""
    
    # if the object is neither a file or a location, return False.
    if not os.path.exists(location) and not os.path.isfile(location):
        print '{Exists} '+location + ' is not a valid file or folder!'
        sys.exit()
        return(False)
    
    #otherwise, return True.
    return(True)

#=========================================================================================
def IsRaster(filename):

    """ Verifies that input filename exists, and is of raster format"""

    import os
    
    rast_types=['bil','bip','bmp','bsq','dat','gif','img','jpg','jp2','png','tif',
                'BIL','BIP','BMP','BSQ','DAT','GIF','IMG','JPG','JP2','PNG','TIF']
    ext=filename[-3:]

    if os.path.isfile(filename):
        for rast_type in rast_types:
            if ext == rast_type:
                return(True)

    return(False)

#=========================================================================================
def Create_Outname(outdir, inname, suffix, ext = False):

    """
    Quick way to create unique output filenames within iterative functions

     This function is built to simplify the creation of output filenames. Function allows
     outdir = False and will create an outname in the same directory as inname. Function will
     add a the user input suffix, separated by an underscore "_" to generate an output name.
     this is usefull when performing a small modification to a file and saving new output with
     a new suffix. function returns an output name, it does not save the file as that name.


     Inputs:
       outdir      either the directory of the desired outname or False to create an outname
                   in the same directory as the inname
       inname      the input file from which to generate the output name "outname"
       suffix      suffix to attach to the end of the filename to mark it as output
       ext         specify the file extension of the output filename. Leave blank or False
                   and the outname will inherit the same extension as inname

     Example Usage:
       outdir = r"C:\Users\jwely\Desktop\output"
       inname = r"C:\Users\jwely\Desktop\folder\subfolder\Landsat_tile.tif"
       suffix = "adjusted"
       outname = core.Create_Outname(outdir,inname,suffix)

       will set outname equal to "C:\Users\jwely\Desktop\output\Landsat_tile_adjusted.tif" which
       can be passed to other functions that require an output filepath.
    """
    
    # isolate the filename from its directory and extension
    head,tail = os.path.split(inname)
    noext = tail.split('.')[:-1]
    noext='.'.join(noext)

    # create the suffix
    if ext:
        suffix = "_{0}.{1}".format(suffix,ext)
    else:
        ext = tail.split('.')[-1:]
        suffix = "_{0}.{1}".format(suffix,''.join(ext))

    if outdir:    
        outname=os.path.join(outdir,noext+suffix)
        return(outname)
    else:
        outname=os.path.join(head,noext+suffix)
        return(outname)

#=========================================================================================
def Date_to_Julian(year,month,day):

    """
    Converts a conventional date to julian day and year
    
     Inputs:
       year        the current year (maters for leap years). string or int
       month       the month of the year. string or int.
       day         the day of the month. string or int.

     Outputs:
       day         date-day for input julian day

     Example usage:
       for december 5th of the year you would type.
       julian_day = Date_to_Julian(2014,12,5)
    """

    import datetime
    
    fmt = "%Y.%m.%d"
    info = datetime.datetime.strptime('.'.join([str(year),str(month),str(day)]),fmt)
    julian_day = info.strftime('%j')

    return(julian_day)

#=========================================================================================
def Julian_to_Date(year,j_day):

    """
    Converts a julian day of the year to conventional date format.

     Inputs:
       year        the current year (maters for leap years)
       j_day       the julian day to convert to a date for given year

     Outputs:
       month       month of input julian day
       day         date-day for input julian day

     Example usage:
       for the 399th day of the year 2014 you would type
               month,day = Julian_to_Date(2014,399)
    """
    
    import datetime
    
    fmt = "%Y.%j"
    info = datetime.datetime.strptime('.'.join([str(year),str(j_day)]),fmt)
    month = info.strftime('%m')
    day = info.strftime('%d')
    
    return(month,day)

#=========================================================================================
def check_module(module_name):

    """
    Checks for module installation and guides user to download source if not found

     Simple function that directs the user to download the input module if they do
     not already have it before returning a "False" value. This helps novice users quickly
     identify that a missing module is the problem and attempt to correct it.

     modules with supported download help links are listed below
     module_list=['h5py','numpy','dbfpy','scipy','matplotlib','PIL','gdal']

     Example usage:
       if check_module('numpy'): import numpy
    """

    module_list=['h5py','numpy','dbfpy','scipy','matplotlib','PIL','gdal','pyhdf']
    
    import webbrowser,time,sys

    # try to import the module, if it works return True, otherwise continue
    try:
        modules = map(__import__,[module_name])
        return(True)
    except:

        for module in module_list:
            if module_name==module:
                print "You do not have " + module_name + ", opening download page for python 2.7 version!"

        # determine the correct url based on module name
        if module_name=='h5py':
            url='https://pypi.python.org/pypi/h5py'
    
        elif module_name=='numpy':
            url='http://sourceforge.net/projects/numpy/files/latest/download?source=files'
    
        elif module_name=='dbfpy':
            url='http://sourceforge.net/projects/dbfpy/files/latest/download'

        elif module_name=='pyhdf':
            url='http://hdfeos.org/software/pyhdf.php'
    
        elif module_name=='scipy':
            url='http://sourceforge.net/projects/scipy/files/latest/download?source=files'
    
        elif module_name=='matplotlib':
            url="""http://sourceforge.net/projects/matplotlib/files/matplotlib/
            matplotlib-1.4.1/windows/matplotlib-1.4.1.win-amd64-py2.7.exe/
            download?use_mirror=superb-dca3"""
    
        elif module_name=='PIL':
            url='http://www.pythonware.com/products/pil/'
    
        elif module_name=='gdal':
            print 'Follow this tutorial closely for installing gdal for 32 bit UNLESS you have intentionally installed 64 bit python'
            url='http://pythongisandstuff.wordpress.com/2011/07/07/installing-gdal-and-ogr-for-python-on-windows/'

        # open the url and HALT operation.
        time.sleep(3)
        webbrowser.open(url)
        sys.exit()
        return(False)
if check_module('numpy'): import numpy
