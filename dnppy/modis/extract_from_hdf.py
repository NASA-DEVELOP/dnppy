# local imports
from dnppy import core
from define_projection import define_projection

import os
import arcpy


def extract_from_hdf(file_list, layer_list, layer_names = False, outdir = None):
    """
    Extracts tifs from MODIS HDF files, ensures proper projection.

    :param file_list:    either a list of '.hdf' files from which data should be extracted,
                         or a directory containing '.hdf'  files.
    :param layer_list:   list of layer numbers to pull out as individual tifs should be integers
                         such as [0,4] for the 0th and 4th layer respectively.
    :param layer_names:  list of layer names to put more descriptive file suffixes to each layer
    :param outdir:       directory to which tif files should be saved
                         if outdir is left as 'None', files are saved in the same directory as
                         the input file was found.

    :return output_filelist: returns a list of all files created by this function
    """

    if outdir is not None:
        if not os.path.exists(outdir):
            os.makedirs(outdir)

    # enforce lists for iteration purposes and sanitize inputs
    file_list = core.enf_filelist(file_list)

    
    for filename in file_list:
        if '.xml' in filename or '.ovr' in filename or not '.hdf' in filename:
            file_list.remove(filename)
            
    layer_list  = core.enf_list(layer_list)
    layer_names = core.enf_list(layer_names)
    
    # ignore user input layer_names if they are invalid, but print warnings
    if layer_names and not len(layer_names) == len(layer_list):
        Warning('layer_names must be the same length as layer_list!')
        Warning('Omitting user defined layer_names!')
        layer_names = False

    output_filelist = []

    # iterate through every file in the input file_list
    for infile in file_list:
        
        # pull the filename and path apart 
        path,name = os.path.split(infile)
        arcpy.env.workspace = path

        for i, layer in enumerate(layer_list):
            
            # specify the layer names.
            if layer_names:
                layername = layer_names[i]
            else:
                layername = str(layer).zfill(3)

            # use the input output directory if the user input one, otherwise build one  
            if outdir:
                outname = os.path.join(outdir, "{0}_{1}.tif".format(name[:-4], layername))
            else:
                outname = os.path.join(path, "{0}_{1}.tif".format(name[:-4], layername))

            # perform the extracting and projection definition
            try:
                arcpy.ExtractSubDataset_management(infile, outname, str(layer))
                define_projection(outname)
                output_filelist.append(outname)

                print("Extracted {0}".format(os.path.basename(outname)))
            except:
                print("Failed to extract {0} from {1}".format(os.path.basename(outname),
                                                               os.path.basename(infile)))

    return output_filelist


if __name__ == "__main__":
    extract_from_hdf(r"C:\Users\jwely\Desktop\Team_Projects\2015_summer_Alaska_Disasters",
                     [0, 1, 2, 3, 4],
                     outdir = r"C:\Users\jwely\Desktop\troubleshooting\test\MOD10A1\frac_snow")
