"""======================================================================================
 The "convert.py" module is part of the "dnppy" package (develop national program py).
 This module houses python functions for converting between data types.

 If you wrote a function you think should be added to this module, or have an idea for one
 you wish was available, please email the Geoinformatics YP class or code it up yourself
 for future DEVELOP participants to use!

"""
#--------------------------------------------------------------------------------------
#           function name           development notes
#--------------------------------------------------------------------------------------
__all__=['Extract_HDF5',        # planned development
         'NetCDF_to_Raster',    # working with bugs
         'Extract_HDF']         # complete

#=========================================================================================
# attempt to import all the common modules and settings
import arcpy,core,sys,os,time

if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    from arcpy.sa import *
    from arcpy import env
    arcpy.env.overwriteOutput = True
#=========================================================================================
def Extract_HDF5(filelist,outdir=False,Quiet=False):

    """
    Function extracts tifs from HDF5s such as IMERG, GMP data.

     inputs:
       filelist    list of '.hdf' files from which data should be extracted
       layerlist   list of layer numbers to pull out as individual tifs
       layernames  list of layer names to put more descriptive names to each layer
       outdir      directory to which tif files should be saved
                   if outdir is left as 'False', files are saved in the same directory as
                   the input file was found.
    """

    # import modules
    if check_module('h5py'): import h5py
    if check_module('numpy'): import numpy

    # set up lists
    failed=[]

    for filename in filelist:
        f=h5py.File(filename,'r')
        print '{Extract_HDF5} This function is unfinished!'

    if not Quiet:print '{Extract_HDF5} Finished!'   
    return(failed)

#=========================================================================================
def NetCDF_to_Raster(filelist,outdir,Quiet=False):

    """
     Function converts NetCDFs to tiffs. Designed to work with TRMM data.

     inputs:
       filelist    list of '.nc' files to conver to tifs.
       outdir      directory to which tif files should be saved

     Bugs:
       does not work with CMIP3 and CMIP5 netcdf's

     Authors: Fall2014: Jeffry Ely
    """

    # Set up initial parameters.
    arcpy.env.workspace = outdir
    filelist=core.Enforce_List(filelist)
    failed=[]

    # convert every file in the list "filelist"
    for infile in filelist:
        
        # use arcpy module to make raster layer from netcdf
        arcpy.MakeNetCDFRasterLayer_md(infile, "r", "longitude", "latitude", "r", "", "", "BY_VALUE")
        arcpy.CopyRaster_management("r", infile[:-3] + ".tif", "", "", "", "NONE", "NONE", "")
        if not Quiet:
            print '{NetCDF_to_Raster} Converted netCDF file ' + infile + ' to Raster'

                
    if not Quiet:print '{NetCDF_to_Raster} Finished!'     
    return (failed)

#=========================================================================================
def Extract_HDF(filelist,layerlist,layernames=False,outdir=False,Quiet=False):

    """
     Function extracts tifs from HDFs.
     Use "Extract_MODIS_HDF" in the modis module for better
     handling of MODIS data with sinusoidal projections.

     inputs:
       filelist    list of '.hdf' files from which data should be extracted
       layerlist   list of layer numbers to pull out as individual tifs should be integers
                   such as [0,4] for the 0th and 4th layer respectively.
       layernames  list of layer names to put more descriptive names to each layer
       outdir      directory to which tif files should be saved
                   if outdir is left as 'False', files are saved in the same directory as
                   the input file was found.

     Authors: Fall2014: Jeffry Ely
    """


    # Set up initial arcpy modules, workspace, and parameters, and sanitize inputs.
    core.Check_Spatial_Extension()
    arcpy.env.overwriteOutput = True

    # enforce lists for iteration purposes
    filelist=core.Enforce_List(filelist)
    layerlist=core.Enforce_List(layerlist)
    layernames=core.Enforce_List(layernames)
    
    # ignore user input layernames if they are invalid, but print warnings
    if layernames and not len(layernames)==len(layerlist):
        print '{Extract_HDF} layernames must be the same length as layerlist!'
        print '{Extract_HDF} ommiting user defined layernames!'
        layernames=False

    # create empty list to add failed file names into
    failed=[]

    # iterate through every file in the input filelist
    for infile in filelist:
        # pull the filename and path apart 
        path,name = os.path.split(infile)
        arcpy.env.workspace = path

        for i in range(len(layerlist)):
            layer=layerlist[i]
            
            # specify the layer names.
            if layernames:
                layername=layernames[i]
            else:
                layername=str(layer).zfill(3)

            # use the input output directory if the user input one, otherwise build one  
            if outdir:
                if not os.path.exists(os.path.join(outdir,layername)):
                    os.makedirs(os.path.join(outdir,layername))
                outname=os.path.join(outdir,layername,name[:-4] +'_'+ layername +'.tif')
            else:
                if not os.path.exists(os.path.join(path,layername)):
                    os.makedirs(os.path.join(path,layername))
                outname=os.path.join(path,layername,name[:-4] +'_'+ layername +'.tif')

            # perform the extracting and projection definition
            try:
                # extract the subdataset
                arcpy.ExtractSubDataset_management(infile, outname, str(layer))
                
                if not Quiet:
                    print '{Extract_HDF} Extracted ' + outname
            except:
                if not Quiet:
                    print '{Extract_HDF} Failed extract '+ outname + ' from ' + infile
                failed.append(infile)
                
    if not Quiet:print '{Extract_HDF} Finished!' 
    return(failed)
