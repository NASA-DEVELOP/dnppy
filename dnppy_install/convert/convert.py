"""
======================================================================================
                                   dnppy.convert
======================================================================================
 This script is part of (dnppy) or "DEVELOP National Program py"
 It is maintained by the Geoinformatics YP class.

It contains functions for misc conversion between formats and types. 
"""

__author__ = ["Jeffry Ely, jeff.ely.08@gmail.com"]


__all__=['HDF5',            # planned development
         'TRMM_NetCDF',     # working with bugs
         'GCMO_NetCDF',     # complete
         'HDF']             # complete


# attempt to import all the common modules and settings
import sys
import os
import time
from dnppy import core

import arcpy
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    from arcpy.sa import *
    from arcpy import env
    arcpy.env.overwriteOutput = True
#========================================================================================


def HDF5(filelist, outdir=False):

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
    if core.check_module('h5py'): import h5py
    if core.check_module('numpy'): import numpy

    # set up lists
    failed=[]

    for filename in filelist:
        f = h5py.File(filename,'r')
        print '{HDF5} This function is unfinished!'

    return(failed)



def TRMM_NetCDF(filelist, outdir):

    """
     Function converts NetCDFs to tiffs. Designed to work with TRMM data.

     inputs:
       filelist    list of '.nc' files to conver to tifs.
       outdir      directory to which tif files should be saved
    """

    # Set up initial parameters.
    arcpy.env.workspace = outdir
    filelist    = core.enforce_list(filelist)

    # convert every file in the list "filelist"
    for infile in filelist:
        
        # use arcpy module to make raster layer from netcdf
        arcpy.MakeNetCDFRasterLayer_md(infile, "r", "longitude", "latitude", "r", "", "", "BY_VALUE")
        arcpy.CopyRaster_management("r", infile[:-3] + ".tif", "", "", "", "NONE", "NONE", "")
        print('{NetCDF} Converted netCDF file ' + infile + ' to Raster')

    return


def GCMO_NetCDF(netcdf_list, variable, outdir):
    """
    Extracts all time layers from a "Global Climate Model Output" NetCDF layer

    Inputs:
        netcdf_list     list of netcdfs from CORDEX climate distribution
        varaible        the climate variable of interest (tsmax, tsmin, etc)
        outdir          output directory to save files.
    """

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    for netcdf in netcdf_list:
        # get net cdf properties object
        props = arcpy.NetCDFFileProperties(netcdf)
        
        print("finding dimensions")
        dims  = props.getDimensions()
        for dim in dims:
            print dim, props.getDimensionSize(dim)

        # make sure the variable is in this netcdf
        if variable:
            if not variable in props.getVariables():
                print("Valid variables for this file include {0}".format(props.getVariables()))
                raise Exception("Variable '{0}' is not in this netcdf!".format(variable))

        for dim in dims:
            if dim == "time":

                # set other dimensions
                x_dim = "lon"
                y_dim = "lat"
                band_dim = ""
                valueSelectionMethod = "BY_VALUE"
                
                size = props.getDimensionSize(dim)
                for i in range(size):

                    # sanitize the dimname for invalid characters
                    dimname = props.getDimensionValue(dim,i).replace(" 12:00:00 PM","")
                    dimname = dimname.replace("/","-").replace(" ","_")
                    
                    dim_value = [["time", props.getDimensionValue(dim,i)]]
                    print("extracting '{0}' from '{1}'".format(variable, dim_value))

                    outname = core.create_outname(outdir, netcdf, dimname, 'tif')
                    
                    arcpy.MakeNetCDFRasterLayer_md(netcdf, variable, x_dim, y_dim, "temp",
                                                   band_dim, dim_value, valueSelectionMethod)
                    arcpy.CopyRaster_management("temp", outname, "", "", "", "NONE", "NONE", "")
                    
    return


def HDF(filelist, layerlist, layernames=False, outdir=False):

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
    """


    # Set up initial arcpy modules, workspace, and parameters, and sanitize inputs.
    core.Check_Spatial_Extension()
    arcpy.env.overwriteOutput = True

    # enforce lists for iteration purposes
    filelist = core.enforce_list(filelist)
    layerlist = core.enforce_list(layerlist)
    layernames = core.enforce_list(layernames)
    
    # ignore user input layernames if they are invalid, but print warnings
    if layernames and not len(layernames) == len(layerlist):
        print('layernames must be the same length as layerlist!')
        print('ommiting user defined layernames!')
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
                layername = layernames[i]
            else:
                layername = str(layer).zfill(3)

            # use the input output directory if the user input one, otherwise build one  
            if outdir:
                if not os.path.exists(os.path.join(outdir,layername)):
                    os.makedirs(os.path.join(outdir,layername))
                outname=os.path.join(outdir,layername,name[:-4] +'_'+ layername +'.tif')
            else:
                if not os.path.exists(os.path.join(path,layername)):
                    os.makedirs(os.path.join(path,layername))
                outname = os.path.join(path,layername,name[:-4] +'_'+ layername +'.tif')

            # perform the extracting and projection definition
            try:
                # extract the subdataset
                arcpy.ExtractSubDataset_management(infile, outname, str(layer))
                
                print('Extracted ' + outname)
            except:
                print('Failed extract '+ outname + ' from ' + infile)
                
                failed.append(infile)
    return(failed)

