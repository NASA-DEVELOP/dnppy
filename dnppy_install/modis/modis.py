"""
======================================================================================
                                   dnppy.modis
======================================================================================

Collection of functions for handling the common MODIS data products

"""

__author__ = ["Jeffry Ely, jeff.ely.08@gmail.com"]

__all__=['Mosaic_MODIS',                # complete
         'Define_MODIS_Projection',     # complete
         'Extract_MODIS_HDF']           # complete

# import modules
import sys, os,time
from dnppy import core

import arcpy
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    from arcpy import sa,env
    arcpy.env.overwriteOutput = True

#======================================================================================
def Mosaic_MODIS(filelist, outdir=False, pixel_type="32_BIT_FLOAT", bands="1",
                                        m_method="LAST", m_colormap="FIRST",Quiet=False):

    """
    Automatically identify appropriate files and mosaic them.

     This script will find and mosaic all MODIS tiles groups with different time names in a
     directory. It will automatically identify the date ranges in the MODIS filenames and
     iterate through the entire range while skipping dates for which there are not at least
     two tiles. Users should be mindful of file suffixes from previous processing.

     This script centers around the 'arcpy.MosaicToNewRaster_management' tool
     [http://help.arcgis.com/en/arcgisdesktop/10.0/help/index.html#//001700000098000000]

     Inputs:
       filelist        the directory containing MODIS data or a list of modis files.
       pixel_type      exactly as the input for the MosaicToNewRaster_management tool.
                       defaults to "32_BIT_FLOAT"
       bands           exactly as the input for the MosaicToNewRaster_management tool.
                       defaults to 1
       m_method        exactly as the input for the MosaicToNewRaster_management tool.
                       defaults to "LAST"
       m_colormap      exactly as the input for the MosaicToNewRaster_management tool.
                       defaults to "FIRST"
       outdir          the directory to save output files to. If none is specified, a
                       default directory will be created as '[indir]_Mosaicked'

     Outputs:
       failed          mosaic opperations which failed due to one or more missing tiles

     Example usage:

           import ND
           indir=      r'C:\Users\jwely\Desktop\Shortcuts\Testbed\Test tiles\MODIS LST\2013\day'
           pixel_type= "16_BIT_UNSIGNED"
           bands=      "1"
           m_method=   "LAST"
           m_colormap= "FIRST"

           ND.Mosaic_MODIS_Dir(indir,pixel_type,bands,m_method,m_colormap,'day')

     Authors: Fall2014: Jeffry Ely
    """

    # typically unchanged parameters of raster dataset. Change at will.
    coordinatesys="#"
    cellsize="#"

    # Set up initial arcpy modules, workspace, and parameters, and sanitize inputs.
    if outdir: OUT=outdir
    filelist=core.Enforce_Rasterlist(filelist)

    # initialize empty lists for tracking
    mosaiclist=[]
    yearlist=[]
    daylist=[]
    productlist=[]
    tilelist=[]
    suffixlist=[]
    failed=[]

    # grab info from all the files left in the filelist.
    for item in filelist:
        info=core.Grab_Data_Info(item,False,True)
        yearlist.append(int(info.year))
        daylist.append(int(info.j_day))

        # find all tiles being represented
        if info.tile not in tilelist:
            tilelist.append(info.tile)
            
        # find all MODIS products existing
        if info.product not in productlist:
            productlist.append(info.product)

        # find all suffixes being represented
        if info.suffix not in suffixlist:
            suffixlist.append(info.suffix)
            
    # define the range of years and days to look for
    years=range(min(yearlist),max(yearlist)+1)
    days=range(min(daylist),max(daylist)+1)

    # print some status updates to the screen
    if not Quiet:
        print '{Mosaic_MODIS} Found tiles : ' + str(tilelist)
        print '{Mosaic_MODIS} Found tiles from years: ' + str(years)
        print '{Mosaic_MODIS} Found tiles from days:  ' + str(days)
        print '{Mosaic_MODIS} Found tiles from product: ' + str(productlist)
        print '{Mosaic_MODIS} Found tiles with suffixes: ' + str(suffixlist)
    #.....................................................................................
    # now that we know what to look for, lets go back through and mosaic everything
    for suffix in suffixlist:
        for product in productlist:
            for year in years:
                for day in days:

                    # build the search criteria
                    search=[(product +'.A'+ str(year)+str(day).zfill(3))]
                    
                    # find files meeting the criteria and sanitize list from accidental metadata inclusions
                    for filename in filelist:
                        if all(x in filename for x in ['.tif'] + search + [suffix]):
                            if not any(x in filename for x in ['.aux','.xml','.ovr','mosaic']):
                                mosaiclist.append(filename)
                    

                    # only continue with the mosaic if more than one file was found!
                    if len(mosaiclist)>1:
                    
                        # if user did not specify an outdir, make folder next to first mosaic file
                        if not outdir:
                            head,tail=os.path.split(mosaiclist[0])
                            OUT=os.path.join(head,'Mosaicked')

                        # make the output directory if it doesnt exist already    
                        if not os.path.isdir(OUT):
                            os.makedirs(OUT)

                        # grab suffix from input files for better naming of output files
                        info=core.Grab_Data_Info(mosaiclist[0],False,True)
                        
                        # define the output name based on input criteria
                        path,filename= os.path.split(mosaiclist[0])
                        outname = filename.replace(info.tile,'mosaic')
                        
                        # perform the mosaic!
                        try:
                            arcpy.MosaicToNewRaster_management(mosaiclist,OUT,\
                                outname,coordinatesys,pixel_type,cellsize,bands,\
                                m_method,m_colormap)
                            
                            # make sure the mosaic list is empty!
                            if not Quiet: print "{Mosaic_MODIS} mosaciked ",outname
                            
                        except:
                            if not Quiet: print "{Mosaic_MODIS} Failed to mosaic files! ",outname
                            failed=failed+mosaiclist
                            
                    # do not attempt a mosaic if only one tile on given day exists!    
                    elif len(mosaiclist)==1:
                        if not Quiet:
                            print("{Mosaic_MODIS} More than one file is required for mosaicing!: "
                                  + str(search))
                        failed=failed+mosaiclist

                    # delete the list of search parameters for this mosaic operation
                    del search[:]
                    del mosaiclist[:]

                    
    if not Quiet:print "{Mosaic_MODIS} Finished! \n"
    return(failed)

#======================================================================================
def Define_MODIS_Projection(filename):

    """Give raster proper MODIS sinusoidal projection metadata"""
    
    # custom text for MODIS sinusoidal projection
    proj= """PROJCS["Sinusoidal",
                GEOGCS["GCS_Undefined",
                    DATUM["D_Undefined",
                        SPHEROID["User_Defined_Spheroid",6371007.181,0.0]],
                    PRIMEM["Greenwich",0.0],
                    UNIT["Degree",0.017453292519943295]],
                PROJECTION["Sinusoidal"],
                PARAMETER["False_Easting",0.0],
                PARAMETER["False_Northing",0.0],
                PARAMETER["Central_Meridian",0.0],
                UNIT["Meter",1.0]]"""

    arcpy.DefineProjection_management(filename,proj)

    return

#======================================================================================
def Extract_MODIS_HDF(filelist,layerlist,layernames=False,outdir=False,Quiet=False):

    """
    Extracts tifs from MODIS HDF files

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

    # enforce lists for iteration purposes and sanitize inputs
    filelist = core.Enforce_Filelist(filelist)
    for filename in filelist:
        if '.xml' in filename:
            filelist.remove(filename)
            
    layerlist=core.Enforce_List(layerlist)
    layernames=core.Enforce_List(layernames)
    
    # ignore user input layernames if they are invalid, but print warnings
    if layernames and not len(layernames)==len(layerlist):
        print '{Extract_MODIS_HDF} layernames must be the same length as layerlist!'
        print '{Extract_MODIS_HDF} ommiting user defined layernames!'
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
                
                # define the projection as the MODIS Sinusoidal
                Define_MODIS_Projection(outname)
                
                if not Quiet:
                    print '{Extract_MODIS_HDF} Extracted ' + outname
            except:
                if not Quiet:
                    print '{Extract_MODIS_HDF} Failed extract '+ outname + ' from ' + infile
                failed.append(infile)
                
    if not Quiet:print '{Extract_MODIS_HDF} Finished! \n' 
    return(failed)
