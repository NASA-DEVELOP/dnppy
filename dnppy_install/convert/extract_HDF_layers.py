
# standard imports
import os
from dnppy import core
import arcpy
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    arcpy.env.overwriteOutput = True

def extract_HDF_layers(filelist, layerlist, layernames = None, outdir = None):

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
    arcpy.env.overwriteOutput = True

    # enforce lists for iteration purposes
    filelist = core.enf_list(filelist)
    layerlist = core.enf_list(layerlist)
    layernames = core.enf_list(layernames)
    
    # ignore user input layernames if they are invalid, but print warnings
    if layernames and not len(layernames) == len(layerlist):
        print('layernames must be the same length as layerlist!')
        print('ommiting user defined layernames!')
        layernames=False

    # create empty list to add filenames into
    produced_files = []

    # iterate through every file in the input filelist
    for infile in filelist:
        # pull the filename and path apart 
        path,name = os.path.split(infile)
        arcpy.env.workspace = path

        for i in range(len(layerlist)):
            layer=layerlist[i]
            
            # specify the layer names.
            if layernames is not None:
                layername = layernames[i]
            else:
                layername = str(layer).zfill(3)

            # use the input output directory if the user input one, otherwise build one  
            if outdir is not None:
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
                produced_files.append(outname)
            except:
                print('Failed extract '+ outname + ' from ' + infile)

    return produced_files


# testing area
if __name__ == "__main__":
    pass