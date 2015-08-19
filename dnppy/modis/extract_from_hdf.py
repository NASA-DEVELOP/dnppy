# local imports
from dnppy import core
from define_projection import define_projection

import os
import arcpy


def extract_from_hdf(filelist, layerlist, layernames = False, outdir = None):

    """
    Extracts tifs from MODIS extract_HDF_layer files, ensures proper projection.

     inputs:
       filelist    list of '.hdf' files from which data should be extracted (or a directory)
       layerlist   list of layer numbers to pull out as individual tifs should be integers
                   such as [0,4] for the 0th and 4th layer respectively.
       layernames  list of layer names to put more descriptive file suffixes to each layer
       outdir      directory to which tif files should be saved
                   if outdir is left as 'False', files are saved in the same directory as
                   the input file was found.
    """

    if outdir is not None:
        if not os.path.exists(outdir):
            os.makedirs(outdir)

    # enforce lists for iteration purposes and sanitize inputs
    filelist = core.enf_filelist(filelist)

    
    for filename in filelist:
        if '.xml' in filename or '.ovr' in filename or not '.hdf' in filename:
            filelist.remove(filename)
            
    layerlist  = core.enf_list(layerlist)
    layernames = core.enf_list(layernames)
    
    # ignore user input layernames if they are invalid, but print warnings
    if layernames and not len(layernames) == len(layerlist):
        Warning('Layernames must be the same length as layerlist!')
        Warning('Ommiting user defined layernames!')
        layernames = False

    # create empty list to add failed file names into
    failed = []

    # iterate through every file in the input filelist
    for infile in filelist:
        
        # pull the filename and path apart 
        path,name           = os.path.split(infile)
        arcpy.env.workspace = path

        for i,layer in enumerate(layerlist):
            
            # specify the layer names.
            if layernames:
                layername = layernames[i]
            else:
                layername = str(layer).zfill(3)

            # use the input output directory if the user input one, otherwise build one  
            if outdir:
                outname = os.path.join(outdir, "{0}_{1}.tif".format(name[:-4], layername))
            else:
                outname = os.path.join(path, "{0}_{1}.tif".format(name[:-4], layername))

            # perform the extracting and projection definition
            try:
                # extract the subdataset
                arcpy.ExtractSubDataset_management(infile, outname, str(layer))

                # define the projection as the MODIS Sinusoidal
                define_projection(outname)

                print("Extracted {0}".format(os.path.basename(outname)))

            except:
                print("Failed to extract {0}  from {1}".format(os.path.basename(outname),
                                                               os.path.basename(infile)))
            failed.append(infile)
                
    print("Finished extracting all hdfs! \n") 
    return failed


if __name__ == "__main__":
    extract_from_hdf(r"C:\Users\jwely\Desktop\Team_Projects\2015_summer_Alaska_Disasters",
                     [0, 1, 2, 3, 4],
                     outdir = r"C:\Users\jwely\Desktop\troubleshooting\test\MOD10A1\frac_snow")
